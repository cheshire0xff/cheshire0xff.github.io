from __future__ import annotations

import datetime
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mako.lookup import TemplateLookup

from . import content, feeds
from .models import LANG_NAMES, Entry, Site, slugify_tag

SECTION_TITLES = {"stories": "Stories", "blog": "Blog", "opinions": "Opinions"}
NAV = [
    ("/stories/", "Stories"),
    ("/blog/", "Blog"),
    ("/opinions/", "Opinions"),
    ("/links/", "Links"),
    ("/about/", "About"),
]


@dataclass(frozen=True)
class Page:
    title: str
    path: str
    lang: str = "en"
    description: str = ""
    alternates: tuple[tuple[str, str], ...] = ()


class Builder:
    def __init__(self, site: Site) -> None:
        self.site = site
        self.lookup = TemplateLookup(
            directories=[str(site.templates_dir)],
            input_encoding="utf-8",
            default_filters=["h"],
        )
        self.written: list[str] = []

    def write(self, url_path: str, html: str) -> None:
        target = self.site.dist_dir / url_path.strip("/") / "index.html"
        self.write_file(target, html)
        self.written.append(url_path)

    @staticmethod
    def write_file(target: Path, text: str) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")

    def render(self, template: str, page: Page, **context: Any) -> str:
        result: str = self.lookup.get_template(template).render(
            site=self.site,
            page=page,
            nav=NAV,
            lang_names=LANG_NAMES,
            tag_slug=slugify_tag,
            **context,
        )
        return result

    def build_entry(self, entry: Entry) -> None:
        alternates = tuple((lang, entry.url(lang)) for lang in entry.langs)
        for lang, variant in entry.variants.items():
            page = Page(
                title=variant.title,
                path=entry.url(lang),
                lang=lang,
                description=variant.summary,
                alternates=alternates if entry.has_translation else (),
            )
            self.write(
                entry.url(lang),
                self.render("post.mako", page, entry=entry, variant=variant),
            )
        assets = entry.source_dir / "assets"
        if assets.is_dir():
            shutil.copytree(
                assets,
                self.site.dist_dir / entry.base_url().strip("/") / "assets",
                dirs_exist_ok=True,
            )

    def build(self) -> list[str]:
        site = self.site
        if site.dist_dir.exists():
            shutil.rmtree(site.dist_dir)
        site.dist_dir.mkdir(parents=True)
        if site.static_dir.is_dir():
            shutil.copytree(site.static_dir, site.dist_dir, dirs_exist_ok=True)

        sections = {name: content.load_section(site.content_dir, name) for name in content.SECTIONS}
        pages = content.load_pages(site.content_dir)
        everything = sorted(
            (entry for entries in sections.values() for entry in entries),
            key=lambda entry: (entry.date or datetime.date.min, entry.slug),
            reverse=True,
        )

        for entry in [*everything, *pages]:
            self.build_entry(entry)

        for name, entries in sections.items():
            page = Page(title=SECTION_TITLES[name], path=f"/{name}/")
            self.write(
                page.path,
                self.render("list.mako", page, heading=page.title, entries=entries),
            )

        tags: dict[str, list[Entry]] = {}
        for entry in everything:
            for tag in entry.tags:
                tags.setdefault(tag, []).append(entry)
        page = Page(title="Tags", path="/tags/")
        self.write(page.path, self.render("tags.mako", page, tags=sorted(tags.items())))
        for tag, entries in tags.items():
            page = Page(title=f"Tag: {tag}", path=f"/tags/{slugify_tag(tag)}/")
            self.write(
                page.path,
                self.render("list.mako", page, heading=f"Tagged “{tag}”", entries=entries),
            )

        home = Page(title=site.title, path="/", description=site.description)
        self.write("/", self.render("index.mako", home, entries=everything[:10]))
        self.write_file(
            site.dist_dir / "404.html",
            self.render("404.mako", Page(title="Not found", path="/404.html")),
        )
        self.write_file(site.dist_dir / "rss.xml", feeds.rss(site, everything[:30]))
        self.write_file(
            site.dist_dir / "sitemap.xml",
            feeds.sitemap(site, self.written),
        )
        return self.written
