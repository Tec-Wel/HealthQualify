# HealthQualify visual design system

**Scope:** Visual presentation and developer experience. No modifications to qualification behavior, safety constraints, or evidence semantics.

## 1. Design direction

HealthQualify should look like a credible engineering product: calm, precise, evidence-oriented, accessible, and self-host friendly. The design references mature open-source developer products but does **not** copy their artwork or proprietary UI.

| Token | Value | Use |
| :--- | :--- | :--- |
| Deep navy | `#102B45` | Banners, chrome, headings |
| Teal | `#0C8579` | Links, focus and positive actions |
| Mint | `#DFF5F1` | Gentle accents, contextual panels |
| Canvas | `#F5F8FC` | Backgrounds |
| Amber | `#E3AB52` | Warnings and caution |
| Body type | System UI (Segoe UI / Arial fallback) | Fast, accessible, zero external font calls |
| Spacing | 4px base; 8/16/24/32px rhythm | Rhythm between headings, tables, and cards |
| Corner radius | 8–16px | Restraint without overly rounded UI |

### Accessibility rules

- Preserve at least 4.5:1 contrast for normal text and visible keyboard focus.
- Use real headings and alt text for every informative image.
- Make links recognizable by more than color alone; descriptive labels.
- Support light/dark mode, reduced motion, responsive tables, and keyboard navigation.
- Don't use badges to substitute for product explanations or verification status.
- Avoid remote fonts, trackers, paid visual plugins, and unreviewed third-party assets.

## 2. Reusable SVG assets

| Asset | Purpose |
| :--- | :--- |
| `assets/healthqualify-home.svg` | Main GitHub landing page hero |
| `assets/visual-product-areas.svg` | Two areas of HealthQualify |
| `assets/agent-release-impact.svg` | Agent 1 icon card |
| `assets/agent-gap-hunter.svg` | Agent 2 icon card |
| `assets/agent-failure-investigation.svg` | Agent 3 icon card |
| `assets/agent-qa-readiness.svg` | Agent 4 icon card |
| `assets/agent-dependency-investigator.svg` | Agent 5 icon card |
| `assets/social-preview.svg` | 2:1 social card source, not installed as GitHub repository settings |

All assets are original, human-readable SVG. SVG cards depict conceptual capabilities rather than proof of executing a particular workflow. GitHub social-preview setting requires repository administration and a raster upload; the SVG here is the source artwork only.

## 3. README rules

- **Top of README:** banner, one-sentence value, clear first-run CTA, docs CTA, alpha notice.
- **Two product areas:** AI investigation and deterministic qualification in a two-column summary.
- **Demo:** copy-ready syntax and an honest note that 2 PASS/5 FAIL is intentional.
- **Agent visuals:** link each SVG card to the agent guide; never present mock results as measured outcomes.
- **Other content:** move extensive tutorials, schemas, research and safety details to versioned Markdown docs.
- Favor 2–4 purposeful links per area over dense clusters of unrelated links.

GitHub README renders GitHub-flavored Markdown, not arbitrary CSS or scripts. The MkDocs website has separate theme CSS and navigation.

## 4. Screenshot authenticity

The README should display **actual captures from the running synthetic dashboard** only after the following steps:

1. Start the local dashboard on `127.0.0.1` with a random token and synthetic demo data.
2. Use `scripts/capture_agent_dashboard.py` or manually capture the browser with its URL and tokens outside the screenshot.
3. Capture 1440×900 desktop, 768×1024 tablet and 390×844 mobile views.
4. Review all pixels for PHI, tokens, emails, paths or other private details.
5. Commit only explicitly reviewed captures, ideally optimized PNG/WebP.
6. Label screenshots with the exact app version and `Synthetic demo`.
7. Do not invent test outcomes or retouch screens to imply unsupported UI controls.

The repository currently ships diagram illustrations and a reproducible screenshot capture script. **It does not claim that any visual illustration is a captured working dashboard.**

## 5. Site and contribution UX

- Documentation site homepage: [index.md](index.md)
- Five-agent instructions: [AI_AGENTS_GUIDE.md](AI_AGENTS_GUIDE.md)
- Local dashboard setup: [AI_AGENT_DASHBOARD.md](AI_AGENT_DASHBOARD.md)
- Contributor onramp: [CONTRIBUTOR_VISUAL_GUIDE.md](CONTRIBUTOR_VISUAL_GUIDE.md)
- Visual capture: [VISUAL_ASSETS_GUIDE.md](VISUAL_ASSETS_GUIDE.md)

For each PR, check that icons/illustrations, screenshot captions, dark mode, mobile navigation, and GitHub internal links work. Run the documentation build and visual asset checks; retain source-only images under `docs/assets/`.

## 6. Regulatory presentation boundaries

Always identify the project as a **developer alpha using synthetic/public nonsensitive data**. Never portray a mockup as a deployed customer interface, a PASS as FDA compliance, a hash chain as WORM storage, or an AI explanation as QA approval.
