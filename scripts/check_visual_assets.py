"""Zero-dependency SVG and visual-link contracts for HealthQualify."""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs/assets"
REQUIRED = [
    "healthqualify-home.svg",
    "visual-product-areas.svg",
    "social-preview.svg",
    "agent-release-impact.svg",
    "agent-gap-hunter.svg",
    "agent-failure-investigation.svg",
    "agent-qa-readiness.svg",
    "agent-dependency-investigator.svg",
]
SVG = "{http://www.w3.org/2000/svg}"


def run() -> None:
    for filename in REQUIRED:
        path = ASSETS / filename
        svg = ET.parse(path).getroot()
        assert svg.tag == SVG + "svg", f"{filename}: invalid SVG root"
        width, height = int(svg.attrib["width"]), int(svg.attrib["height"])
        assert 0 < width <= 2000 and 0 < height <= 1000, f"{filename}: invalid dimensions"
        assert svg.attrib.get("viewBox"), f"{filename}: missing viewBox"
        title = svg.find(SVG + "title")
        desc = svg.find(SVG + "desc")
        assert title is not None and (title.text or "").strip(), f"{filename}: missing accessible title"
        assert desc is not None and (desc.text or "").strip(), f"{filename}: missing accessible description"
        assert not re.search(r"<script\b|https?://|onload\s*=", path.read_text(), re.I), \
            f"{filename}: external resource or script is not allowed"
        print(f"PASS {filename} [{width}x{height}]")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for filename in REQUIRED:
        if filename == "social-preview.svg":
            continue
        assert f"docs/assets/{filename}" in readme or filename.startswith("agent-"), \
            f"README missing {filename}"
    assert "[docs](docs/" not in readme
    assert "Synthetic developer alpha" in readme
    print("PASS README visual integrity")


if __name__ == "__main__":
    run()
