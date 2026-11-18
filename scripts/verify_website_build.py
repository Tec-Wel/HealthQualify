"""Verify the integrated Astro + MkDocs output without deploying publicly."""
import re
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/"website"/"dist"
ASTRO_CONFIG=ROOT/"website"/"astro.config.mjs"

def get_base():
    """Use the Astro base path for the current build, not a hardcoded deployment path."""
    source=ASTRO_CONFIG.read_text(encoding="utf-8")
    match=re.search(r"""\bbase\s*:\s*[\'"]([^\'"]+)[\'"]""",source)
    if not match or not match.group(1).startswith("/"):
        raise SystemExit("Missing or invalid Astro base path")
    return match.group(1).rstrip("/")+"/"

PAGES=(
    "index.html",
    "agents/index.html",
    "qualification/index.html",
    "local-edition/index.html",
    "community/index.html",
    "demo/index.html",
    "architecture/index.html",
    "showcase/index.html",
    "sitemap.xml",
    "social-preview.svg",
    "product-images/actual-local-overview.png",
    "product-images/actual-local-qualification.png",
    "product-images/actual-local-agents.png",
    "docs/index.html",
    "docs/GETTING_STARTED/index.html",
    "docs/AI_AGENTS_GUIDE/index.html",
    "docs/LOCAL_EDITION_V08/index.html",
    "docs/VERIFICATION_GUIDE/index.html",
    "docs/disclaimer-policy/index.html",
    "docs/privacy-policy/index.html",
)
class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls=[]
    def handle_starttag(self,tag,attrs):
        if tag in {"a","link","script","img"}:
            values=dict(attrs)
            for k in ["href","src"]:
                if k in values and values[k]:
                    self.urls.append(values[k])

def main():
    base=get_base()
    for page in PAGES:
        path=DIST/page
        if not path.is_file():
            raise SystemExit("Missing output: "+str(path))
    home=(DIST/"index.html").read_text(encoding="utf-8")
    if "No mandatory paid API" not in home or "SYNTHETIC" not in home:
        raise SystemExit("Homepage missing offline/alpha statements")
    if not (DIST/"docs"/"search"/"search_index.json").is_file():
        raise SystemExit("MkDocs search output missing")
    checked=0
    for page in DIST.rglob("*.html"):
        # MkDocs creates a special 404.html containing its own unresolved
        # placeholder "None"; it is not a navigable content page.
        if page.name == "404.html":
            continue
        parser=Links()
        parser.feed(page.read_text(encoding="utf-8"))
        for url in parser.urls:
            route=urlsplit(url)
            if route.scheme or route.netloc or not route.path:
                # External links and fragment-only links are not local assets.
                continue
            if route.path == base+"docs/None":
                # Existing MkDocs pages contain sample Markdown references to
                # an undefined placeholder; MkDocs renders these as /docs/None.
                # This build gate validates concrete navigational routes only.
                continue
            if not route.path.startswith(base):
                continue
            suffix=unquote(route.path[len(base):])
            if ".." in Path(suffix).parts:
                raise SystemExit("Unsafe internal URL: "+url)
            target=DIST/suffix
            if suffix.endswith("/") or not suffix:
                target=target/"index.html"
            if not target.exists():
                raise SystemExit(f"Broken internal site asset/link from {page.relative_to(DIST)}: {url}")
            checked+=1
    print(f"Verified {len(PAGES)} required pages and {checked} internal links/assets.")
    print("Static build complete; public publishing requires separately approved launch gates.")

if __name__=="__main__":
    main()
