from __future__ import annotations

import datetime
import re
from pathlib import Path
from typing import Any

import markdown
import yaml

from .models import DEFAULT_LANG, LANG_NAMES, ContentError, Entry, Variant

SECTIONS = ("stories", "blog", "opinions")
PAGES_DIR = "pages"
_FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.DOTALL)


def split_front_matter(text: str, source: Path) -> tuple[dict[str, Any], str]:
    match = _FRONT_MATTER.match(text.lstrip("\ufeff"))
    if match is None:
        raise ContentError(f"{source}: missing front matter")
    meta = yaml.safe_load(match.group(1)) or {}
    if not isinstance(meta, dict):
        raise ContentError(f"{source}: front matter must be a mapping")
    return meta, match.group(2)


def render_markdown(body: str) -> str:
    return markdown.markdown(body, extensions=["extra", "sane_lists"])


def _as_date(value: Any, source: Path) -> datetime.date | None:
    if value is None:
        return None
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    raise ContentError(f"{source}: invalid date {value!r}")


def _as_tags(value: Any, source: Path) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, list) and all(isinstance(tag, str) for tag in value):
        return tuple(value)
    raise ContentError(f"{source}: tags must be a list of strings")


def load_entry(section: str, entry_dir: Path) -> Entry | None:
    variants: dict[str, Variant] = {}
    dates: set[datetime.date] = set()
    tags: set[str] = set()
    original: str | None = None

    for path in sorted(entry_dir.glob("*.md")):
        lang = path.stem
        if lang not in LANG_NAMES:
            raise ContentError(f"{path}: unknown language code {lang!r}")
        meta, body = split_front_matter(path.read_text(encoding="utf-8"), path)
        if meta.get("draft"):
            continue
        title = meta.get("title")
        if not isinstance(title, str) or not title:
            raise ContentError(f"{path}: missing title")
        date = _as_date(meta.get("date"), path)
        if date is not None:
            dates.add(date)
        tags.update(_as_tags(meta.get("tags"), path))
        if meta.get("original") and original is None:
            original = str(meta["original"])
        variants[lang] = Variant(
            lang=lang,
            title=title,
            summary=str(meta.get("summary", "")),
            html=render_markdown(body),
            words=len(re.findall(r"\w+", body)),
        )

    if not variants:
        return None
    if len(dates) > 1:
        raise ContentError(f"{entry_dir}: language files disagree on date")
    if original is None:
        original = DEFAULT_LANG if DEFAULT_LANG in variants else next(iter(variants))
    if original not in variants:
        raise ContentError(f"{entry_dir}: original language {original!r} has no file")
    return Entry(
        section=section,
        slug=entry_dir.name,
        date=next(iter(dates), None),
        tags=tuple(sorted(tags)),
        original=original,
        variants=variants,
        source_dir=entry_dir,
    )


def _load_dir(section: str, directory: Path) -> list[Entry]:
    if not directory.is_dir():
        return []
    entries = (load_entry(section, path) for path in sorted(directory.iterdir()) if path.is_dir())
    return [entry for entry in entries if entry is not None]


def load_section(content_dir: Path, section: str) -> list[Entry]:
    entries = _load_dir(section, content_dir / section)
    return sorted(
        entries, key=lambda entry: (entry.date or datetime.date.min, entry.slug), reverse=True
    )


def load_pages(content_dir: Path) -> list[Entry]:
    return _load_dir("", content_dir / PAGES_DIR)
