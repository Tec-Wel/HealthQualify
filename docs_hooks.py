"""Build-time GitHub-Markdown compatibility for the static documentation site.

Preserves GitHub alert syntax and repository-relative links in source. MkDocs
receives proper Material admonitions and valid links for docs_dir.
"""
from __future__ import annotations

import re

ALERTS = {
    "NOTE": "note",
    "TIP": "tip",
    "IMPORTANT": "important",
    "WARNING": "warning",
    "CAUTION": "danger",
}
START = re.compile(r"^> \[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*$")
BASE = "https://github.com/Tec-Wel/HealthQualify/blob/main/"


def on_page_markdown(markdown, **_kwargs):
    lines = markdown.splitlines()
    output = []
    i = 0
    while i < len(lines):
        match = START.match(lines[i].strip())
        if not match:
            output.append(lines[i])
            i += 1
            continue
        body = []
        kind = ALERTS[match.group(1)]
        i += 1
        while i < len(lines) and lines[i].startswith(">"):
            item = lines[i][1:]
            body.append(item[1:] if item.startswith(" ") else item)
            i += 1
        output.extend(["!!! " + kind, *["    " + line if line else "" for line in body], ""])

    site_markdown = "\n".join(output)
    # README.md within docs/ referred to GitHub's separate documentation
    # landing in older guides. The MkDocs home is docs/index.md.
    site_markdown = re.sub(
        r"(?<=\])\(README\.md(#[^)]*)?\)",
        lambda m: "(index.md" + (m.group(1) or "") + ")",
        site_markdown,
    )
    for name in ("README.md", "CONTRIBUTING.md", "SECURITY.md", "SUPPORT.md", "CHANGELOG.md", "TRADEMARK_POLICY.md"):
        site_markdown = site_markdown.replace("](../" + name + ")", "](" + BASE + name + ")")
    # Files outside docs/ are available in the source repo, not in MkDocs.
    site_markdown = re.sub(
        r"(?<=\])\(\.\./examples/templates/([^)]*)\)",
        lambda m: "(" + BASE + "examples/templates/" + m.group(1) + ")",
        site_markdown,
    )
    return site_markdown
