from __future__ import annotations

import datetime
import math
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

LANG_NAMES: dict[str, str] = {"pl": "Polski", "en": "English"}
WORDS_PER_MINUTE = 220
DEFAULT_LANG = "en"


class ContentError(Exception):
    pass


@dataclass(frozen=True)
class Site:
    title: str = "cheshire0xff"
    description: str = "Short stories, blog posts, opinions and links."
    author: str = "cheshire0xff"
    url: str = field(
        default_factory=lambda: os.environ.get("SITE_URL", "https://cheshire0xff.github.io")
    )
    root: Path = field(default_factory=Path.cwd)

    @property
    def content_dir(self) -> Path:
        return self.root / "content"

    @property
    def templates_dir(self) -> Path:
        return self.root / "templates"

    @property
    def static_dir(self) -> Path:
        return self.root / "static"

    @property
    def dist_dir(self) -> Path:
        return self.root / "dist"


@dataclass(frozen=True)
class Variant:
    lang: str
    title: str
    summary: str
    html: str
    words: int

    @property
    def reading_minutes(self) -> int:
        return max(1, math.ceil(self.words / WORDS_PER_MINUTE))


@dataclass(frozen=True)
class Entry:
    section: str
    slug: str
    date: datetime.date | None
    tags: tuple[str, ...]
    original: str
    variants: dict[str, Variant]
    source_dir: Path

    @property
    def langs(self) -> list[str]:
        return [self.original] + sorted(lang for lang in self.variants if lang != self.original)

    @property
    def has_translation(self) -> bool:
        return len(self.variants) > 1

    def base_url(self) -> str:
        return f"/{self.section}/{self.slug}/" if self.section else f"/{self.slug}/"

    def url(self, lang: str | None = None) -> str:
        if lang is None or lang == self.original:
            return self.base_url()
        return f"{self.base_url()}{lang}/"

    @property
    def main(self) -> Variant:
        return self.variants[self.original]


def slugify_tag(tag: str) -> str:
    return re.sub(r"[^\w]+", "-", tag.strip().lower()).strip("-")
