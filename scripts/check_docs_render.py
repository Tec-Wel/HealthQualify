"""Regression test for *rendered* Material HTML, not only successful build exit.

Catches Markdown accidentally placed inside HTML without markdown="1":
the original defect produced visible '![' images and '[label](path)' text.
"""
from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path


class PageInspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.links = []
        self.headings = []
        self._h1 = False
        self._h1_parts = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "img":
            self.images.append(a.get("alt", ""))
        if tag == "a":
            self.links.append(a.get("href", ""))
        if tag == "h1":
            self._h1 = True
            self._h1_parts = []

    def handle_data(self, data):
        self.text.append(data)
        if self._h1:
            self._h1_parts.append(data)

    def handle_endtag(self, tag):
        if tag == "h1":
            self.headings.append("".join(self._h1_parts).strip())
            self._h1 = False


def check(path: Path, heading: str, hero: str, links: list[str]):
    if not path.is_file():
        raise AssertionError("Missing generated page: " + str(path))
    html = path.read_text(encoding="utf-8")
    p = PageInspector()
    p.feed(html)
    if heading not in p.headings:
        raise AssertionError(f"Unrendered page heading in {path}: {p.headings!r}")
    if hero not in p.images:
        raise AssertionError(f"Hero image Markdown did not render in {path}")
    text = " ".join(p.text)
    if "![" + hero + "]" in text or "[!IMPORTANT]" in text or "[**" in text:
        raise AssertionError("Raw Markdown appears in generated page: " + str(path))
    for href in links:
        if not any(href in x for x in p.links):
            raise AssertionError(f"Expected working navigation link {href} missing in {path}")
    print("PASS", path, "headings:", len(p.headings), "images:", len(p.images))


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "site")
    check(root / "index.html", "Qualify with evidence. Not assumptions.",
          "HealthQualify · Evidence-first qualification",
          ["GETTING_STARTED/", "AI_AGENTS_GUIDE/", "AI_AGENT_DASHBOARD/"])
    check(root / "AI_AGENTS_GUIDE" / "index.html",
          "Meet the five local AI agents",
          "Five HealthQualify local AI agents",
          ["AI_AGENT_DASHBOARD/"])
    check(root / "AI_AGENT_DASHBOARD" / "index.html",
          "The local agent dashboard",
          "HealthQualify local AI agent dashboard",
          ["AI_AGENTS_GUIDE/"])


if __name__ == "__main__":
    main()
