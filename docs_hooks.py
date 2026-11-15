"""Build-only conversion of GitHub alert blockquotes to MkDocs admonitions.

GitHub Markdown retains its native [!IMPORTANT]/[!NOTE] presentation. The
static MkDocs site receives actual Material admonition cards instead of
displaying the GitHub alert marker as literal body text.
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
        kind = ALERTS[match.group(1)]
        body = []
        i += 1
        while i < len(lines) and lines[i].startswith(">"):
            item = lines[i][1:]
            body.append(item[1:] if item.startswith(" ") else item)
            i += 1
        output.extend(["!!! " + kind, *["    " + line if line else "" for line in body], ""])

    site_markdown = "\\n".join(output)
    # Most guides were authored for GitHub, where repository-root links use
    # ../README.md. MkDocs has its own docs/index.md root and cannot serve files
    # from outside docs/. Rewrite only recognized local Markdown link targets.
    site_markdown = re.sub(
        r"(?<=\\])\\((?:README\\.md)(#[^)]*)?\\)",
        lambda m: "(index.md" + (m.group(1) or "") + ")",
        site_markdown,
    )
    root_links = {
        "README.md": "README.md",
        "CONTRIBUTING.md": "CONTRIBUTING.md",
        "SECURITY.md": "SECURITY.md",
        "SUPPORT.md": "SUPPORT.md",
        "CHANGELOG.md": "CHANGELOG.md",
    }
    for name, target in root_links.items():
        site_markdown = site_markdown.replace(
            "](../" + name + ")",
            "](https://github.com/Tec-Wel/HealthQualify/blob/main/" + target + ")",
        )
    # Protocol templates live outside docs_dir and should link to the actual
    # GitHub source rather than generating broken MkDocs document links.
    site_markdown = re.sub(
        r"(?<=\\])\\(\\.\\./examples/templates/([^)]*)\\)",
        lambda m: "](https://github.com/Tec-Wel/HealthQualify/blob/main/examples/templates/" + m.group(1) + ")",
        site_markdown,
    )
    return site_markdown
