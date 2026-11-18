# HealthQualify Web Experience (MONAI-inspired, original design)

A free, original Astro-based, responsive marketing and navigation website for HealthQualify. The **technical documentation remains MkDocs Material** and builds into `/docs/` under the same static website.

**No paid templates, hosted APIs, analytics, externally hosted fonts, or tracking scripts are required.** All application functionality remains in the independent HealthQualify Python repository; this is a static marketing/education site and does not process PHI.

## Local development

Requires Node.js 22+ and Python 3.10+ (Python 3.12 recommended):

```bash
cd website
npm install
npm run dev
```

The local Astro development server previews the marketing site. To build **both** Astro and MkDocs into one output directory:

```bash
cd website
npm run build
cd ..
python -m pip install -r requirements-docs.txt
python -m mkdocs build --site-dir website/dist/docs
python scripts/verify_website_build.py
```

Run `cd website && npm test` for the static website contract tests. GitHub Actions also runs Chromium browser QA at 390px, 768px and 1440px, plus the real local application against temporary synthetic data; screenshots are stored as **private workflow artifacts**. Because the repository remains private and public-launch approvals are pending, HTML meta and robots rules use **noindex / Disallow**. Change those rules only after publication approval.

## Pages

- `/` — product hero, synthetic evidence illustration and product overview
- `/qualification/` — evidence-first qualification capabilities
- `/agents/` — five source-linked draft investigators
- `/local-edition/` — offline-first demo instructions
- `/community/` — contributions, licensing and governance
- `/demo/` — accessible, static synthetic guided tour with no backend
- `/architecture/` — keyboard-operable architecture explorer
- `/showcase/` — links to actual synthetic Local Edition screenshots produced by browser QA
- `/docs/` — existing MkDocs Material technical documentation with search

**Important:** Relative URLs assume the GitHub Pages repository base path `/HealthQualify/`. An alternate host/base path requires updating Astro and MkDocs together.

## Hosting and publishing gates

GitHub Actions workflow `.github/workflows/website-build.yml` creates a downloadable preview artifact. **It does not automatically deploy publicly.** HealthQualify is currently private pending public launch owner/IP, security-history and redistribution review in [Issue #36](https://github.com/Tec-Wel/HealthQualify/issues/36). Do not enable public Pages or mark the alpha as regulated-production ready before the approval gates are closed.

The website’s visual components are independently authored; do not copy MONAI branding, logos, layouts, images, or texts. All first-party source remains under the repository Apache-2.0 licensing, subject to accurate ownership review.
