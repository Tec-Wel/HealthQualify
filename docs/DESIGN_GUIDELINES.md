# Documentation design guidelines

**[← Documentation home](README.md)** · **Visual system** · **For maintainers**

Our docs are designed for GitHub's native Markdown renderer—not custom CSS, JavaScript, or a website framework. The design should feel cohesive and useful without making the content harder to read.

## Page structure

1. A compact category banner that loads from `assets/category-*.svg`.
2. A short breadcrumb leading back to [Documentation home](README.md).
3. One meaningful H1 title, followed by a concise *what you'll learn* summary.
4. A small contextual table of contents with links to real headings where useful.
5. The existing accurate step-by-step technical content and examples.
6. A final **Continue learning** section with 2–3 related guides.

## Visual principles

| Principle | Standard |
| :--- | :--- |
| Navigation | Always provide a one-click route to docs home |
| Visual consistency | Use the same restrained navy/teal SVG brand family |
| Accessibility | Give informative alt text, semantic headings and code fences |
| Scanability | Prefer short summaries, tables, purposeful callouts, and real steps |
| Honest status | Label alpha limitations, future ideas, and intentional negative runs |
| Code examples | Clearly label shell/JSON, identify environment, preserve exit behavior |
| Links | Use relative links to checked-in files, avoid tracking parameters |
| Restraint | Avoid emoji overload, huge badge groups, broken HTML/CSS and decorative link walls |

## Navigation map

- **Start:** [Getting started](GETTING_STARTED.md) · [Installation](INSTALLATION.md)
- **Build:** [Developer architecture](DEVELOPER_ARCHITECTURE.md) · [CLI](CLI_REFERENCE.md)
- **Healthcare:** [Use cases](HEALTHCARE_USE_CASES.md) · [Methodology](QUALIFICATION_METHODOLOGY.md)
- **Trust:** [Security model](SECURITY_MODEL.md) · [Verification](VERIFICATION_GUIDE.md)
- **Agents:** [AI agents](AI_AGENTS_GUIDE.md)
- **Reference:** [Roadmap](ROADMAP.md) · [Release status](RELEASE_STATUS.md)

## How to preview

GitHub automatically renders `docs/README.md` when navigating to the `docs/` directory. The source `DOCUMENTATION_INDEX.md` is a separate navigation entrypoint; keep both aligned. Existing `mkdocs.yml` remains optional and does **not** mean a documentation website is deployed.

Before merging changes, run `python -m unittest discover -s tests -v` and check affected links, diagram rendering and expected synthetic example outcomes. Do not publicly publish a private repository's documentation without an explicit decision.
