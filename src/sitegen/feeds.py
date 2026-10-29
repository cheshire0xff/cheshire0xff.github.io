from __future__ import annotations

import datetime
from email.utils import format_datetime
from xml.etree import ElementTree as ET

from .models import Entry, Site


def _to_xml(root: ET.Element) -> str:
    ET.indent(root)
    body = ET.tostring(root, encoding="unicode")
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{body}\n'


def rss(site: Site, entries: list[Entry]) -> str:
    root = ET.Element("rss", version="2.0")
    channel = ET.SubElement(root, "channel")
    ET.SubElement(channel, "title").text = site.title
    ET.SubElement(channel, "link").text = site.url
    ET.SubElement(channel, "description").text = site.description
    for entry in entries:
        item = ET.SubElement(channel, "item")
        link = site.url + entry.url()
        ET.SubElement(item, "title").text = entry.main.title
        ET.SubElement(item, "link").text = link
        ET.SubElement(item, "guid").text = link
        description = entry.main.summary
        if entry.has_translation:
            others = ", ".join(lang for lang in entry.langs[1:])
            description = f"{description} (also available in: {others})".strip()
        ET.SubElement(item, "description").text = description
        if entry.date is not None:
            moment = datetime.datetime.combine(entry.date, datetime.time(), datetime.UTC)
            ET.SubElement(item, "pubDate").text = format_datetime(moment)
    return _to_xml(root)


def sitemap(site: Site, paths: list[str]) -> str:
    root = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for path in sorted(paths):
        url = ET.SubElement(root, "url")
        ET.SubElement(url, "loc").text = site.url + path
    return _to_xml(root)
