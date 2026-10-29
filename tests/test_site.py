from __future__ import annotations

from pathlib import Path

import pytest

from sitegen.content import load_entry
from sitegen.models import ContentError, Site
from sitegen.render import Builder


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_site(root: Path) -> Site:
    templates = Path(__file__).resolve().parents[1] / "templates"
    (root / "templates").mkdir()
    for template in templates.glob("*.mako"):
        (root / "templates" / template.name).write_text(
            template.read_text(encoding="utf-8"), encoding="utf-8"
        )
    return Site(root=root, url="https://example.test")


def test_single_language_entry(tmp_path: Path) -> None:
    write(tmp_path / "a" / "pl.md", "---\ntitle: Cień\ndate: 2026-01-02\n---\nTekst")
    entry = load_entry("stories", tmp_path / "a")
    assert entry is not None
    assert entry.original == "pl"
    assert not entry.has_translation
    assert entry.url() == "/stories/a/"


def test_translation_detected(tmp_path: Path) -> None:
    write(tmp_path / "a" / "pl.md", "---\ntitle: Cień\n---\nTekst")
    write(tmp_path / "a" / "en.md", "---\ntitle: Shadow\n---\nText")
    entry = load_entry("stories", tmp_path / "a")
    assert entry is not None
    assert entry.has_translation
    assert entry.langs == ["en", "pl"]
    assert entry.url("pl") == "/stories/a/pl/"


def test_original_override(tmp_path: Path) -> None:
    write(tmp_path / "a" / "pl.md", "---\ntitle: Cień\noriginal: pl\n---\nTekst")
    write(tmp_path / "a" / "en.md", "---\ntitle: Shadow\n---\nText")
    entry = load_entry("stories", tmp_path / "a")
    assert entry is not None
    assert entry.langs == ["pl", "en"]
    assert entry.url("en") == "/stories/a/en/"


def test_default_language_is_english(tmp_path: Path) -> None:
    write(tmp_path / "a" / "pl.md", "---\ntitle: Cień\n---\nTekst")
    write(tmp_path / "a" / "en.md", "---\ntitle: Shadow\n---\nText")
    entry = load_entry("stories", tmp_path / "a")
    assert entry is not None
    assert entry.original == "en"
    assert entry.url("pl") == "/stories/a/pl/"


def test_polish_only_entry_stays_polish(tmp_path: Path) -> None:
    write(tmp_path / "a" / "pl.md", "---\ntitle: Cień\n---\nTekst")
    entry = load_entry("stories", tmp_path / "a")
    assert entry is not None
    assert entry.original == "pl"


def test_unknown_language_fails(tmp_path: Path) -> None:
    write(tmp_path / "a" / "xx.md", "---\ntitle: T\n---\nx")
    with pytest.raises(ContentError):
        load_entry("stories", tmp_path / "a")


def test_date_mismatch_fails(tmp_path: Path) -> None:
    write(tmp_path / "a" / "pl.md", "---\ntitle: T\ndate: 2026-01-01\n---\nx")
    write(tmp_path / "a" / "en.md", "---\ntitle: T\ndate: 2026-01-02\n---\nx")
    with pytest.raises(ContentError):
        load_entry("stories", tmp_path / "a")


def test_build_renders_switch_only_with_translation(tmp_path: Path) -> None:
    site = make_site(tmp_path)
    write(tmp_path / "content" / "stories" / "a" / "pl.md", "---\ntitle: A\noriginal: pl\n---\nx")
    write(tmp_path / "content" / "stories" / "a" / "en.md", "---\ntitle: A en\n---\nx")
    write(tmp_path / "content" / "stories" / "b" / "pl.md", "---\ntitle: B\n---\nx")
    Builder(site).build()
    dist = tmp_path / "dist"
    assert 'class="lang-switch"' in (dist / "stories" / "a" / "index.html").read_text("utf-8")
    assert (dist / "stories" / "a" / "en" / "index.html").is_file()
    assert 'class="lang-switch"' not in (dist / "stories" / "b" / "index.html").read_text("utf-8")
    assert (dist / "rss.xml").is_file()
    assert "https://example.test/stories/a/en/" in (dist / "sitemap.xml").read_text("utf-8")
