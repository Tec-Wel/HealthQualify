# HealthQualify documentation website — local setup

**Price:** MkDocs and Material for MkDocs community editions are open source and free. This repository uses no paid plugin, analytics service, hosted search, or purchased domain.

**Publication:** This configuration **builds locally and in CI only**. There is no GitHub Pages deployment action. The repository is currently private; **do not make documentation public or change repository visibility without reviewing the content and confirming authorization**. Building is not publishing.

## Preview the site locally

Python 3.10+ recommended (project CI uses 3.12):

```bash
git clone https://github.com/Tec-Wel/HealthQualify.git
cd HealthQualify
python -m pip install -r requirements-docs.txt
python -m mkdocs serve --dev-addr 127.0.0.1:8000
```

Open **http://127.0.0.1:8000/** on the same workstation. Editing a Markdown file refreshes the local preview.

## Build static pages

```bash
python -m mkdocs build --site-dir site
```

The `site/` directory contains static HTML/CSS/JS. It should remain untracked and should not be exposed until review. The GitHub Actions `Documentation site — build only` workflow uses `/tmp/healthqualify-site` and checks that the index and both AI-agent guides are generated. It does **not** upload or deploy the generated site.

## Navigation & design

Edit `mkdocs.yml` to change the sidebar, tabs, search, palette, and page hierarchy. Markdown pages remain under `docs/`. The main landing page is `docs/DOCUMENTATION_INDEX.md` and the focused AI pages are `docs/AI_AGENTS_GUIDE.md` and `docs/AI_AGENT_DASHBOARD.md`.

The styling lives in `docs/stylesheets/extra.css`; the brand uses navy and teal with accessibility-conscious contrast. Search uses the bundled offline-capable client-side index; search does not send documentation text to a hosted AI provider. The site may still load optional external assets if explicitly added by contributors; review such changes before publishing.

## Future public hosting (not enabled)

GitHub Pages is free from **public** repositories on GitHub Free. Private repository Pages eligibility depends on the owner's plan, and GitHub Pages publication is not automatically private just because the source repository is private. A public documentation deployment requires an explicit access, content, license, repository-visibility, and hosting decision.

For an open-source release, prefer a separately reviewed public docs repository or a public project repository with GitHub Pages, after removing non-public content. Public Pages can use a default `github.io` URL without buying a custom domain. CI usage and paid-account limits vary by plan.

## Maintenance note — Material for MkDocs

The Material for MkDocs maintainers announced security maintenance through **May 5, 2027**, followed by end of upstream maintenance. This is a free, short-term documentation solution, **not** a long-term dependency promise. Review the maintainers' successor **Zensical** and schedule a migration before the maintenance end date. Do not blindly upgrade across incompatible theme versions.

## Governance

The docs are a developer-alpha educational experience, **not** a regulated compliance statement. Use synthetic or public nonsensitive data only. Keep `main` protected through normal PR review and CI checks.
