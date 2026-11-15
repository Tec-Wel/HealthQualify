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
    return "\n".join(output)
