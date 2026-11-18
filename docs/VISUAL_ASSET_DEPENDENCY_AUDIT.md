# HealthQualify visual asset and website dependency provenance audit

**Audit date:** 2026-11-18  
**Reference:** `main` at `67b9f4526e8d47f474b7bdc59631af087caa4e6e` (Git tree).  
**Disposition:** **HOLD — requires authorized maintainer/legal review before public release.** This is a static source inventory, not a legal opinion, original-authorship certification, a visual-comparison clearance, or a complete binary/transitive dependency review.

## Summary

| Scope | Observed result | Interpretation |
|---|---|---|
| Git tree | 264 entries; recursive response not truncated | This is a snapshot of tracked files on `main`, not all historical/release artifacts |
| Checked-in website/docs visual assets | 20 SVGs; no PNG/JPEG/GIF/WebP or font binaries in these folders | Source SVGs examined for external-resource/embed indications; originality is **unverified** |
| Inline SVG content | SVG source uses graphic elements and text; no external bitmap references or external href-based embed observed in inspected assets | Does **not** prove rights, non-infringement or authorship |
| Astro website source | Read website Astro pages, shared layout and CSS | No named competitor inspiration claim identified in current page/layout/style source; this is not visual similarity analysis |
| CSS font policy | `Inter` listed first in CSS fallback stack, no `@font-face`, remote CSS import or bundled font found | Browser may use already-installed Inter, otherwise system fallback; verify design appearance and font policy |
| External links | Observed GitHub project/security/contribution links and site social-preview metadata | These are project links, not unauthorized asset embeds; keep license/technical links |
| Dependency lock | 378 entries including root | Lockfile-declared licenses only; validate upstream license text and actual shipped build contents |
| Third-party licensing | LGPL-related, MIT, Apache-2.0, BSD and other declarations occur | Review component-specific notices and distribution obligations, especially if binaries/assets are bundled |
| Ownership and similarity | No signed inventor/creator statements or independently reviewed visual comparator evidence supplied | **Unresolved: human design and IP review mandatory** |

## Tracked visual asset inventory

The value in the SHA column is **Git's blob object SHA-1**, *not* a legal provenance record or an independent SHA-256 checksum. A public-release asset manifest should additionally include exact file SHA-256 and author/rights evidence.

| Tracked file | Bytes | Git blob SHA-1 | Ownership/provenance status |
|---|---:|---|---|
| `docs/assets/agent-dependency-investigator.svg` | 993 | `bb35c677206a72807dca5803050ddeea187383b7` | **Unverified — human source/author/rights evidence required** |
| `docs/assets/agent-failure-investigation.svg` | 989 | `90885bf230a730bbb3fb80de842619daffa6a9c0` | **Unverified — human source/author/rights evidence required** |
| `docs/assets/agent-gap-hunter.svg` | 970 | `4cc0f8b10cec2d070de4adf5b04327b85852d622` | **Unverified — human source/author/rights evidence required** |
| `docs/assets/agent-qa-readiness.svg` | 961 | `52edf806df40eed380dfad2a86e0982f5879c7a9` | **Unverified — human source/author/rights evidence required** |
| `docs/assets/agent-release-impact.svg` | 976 | `176d45023c154fa18cb8c7b25242542b68e9b488` | **Unverified — human source/author/rights evidence required** |
| `docs/assets/ai-agents-hero.svg` | 2394 | `0806161559ea2fc7fbe09bedc6b6a60c366cff91` | **Unverified — human source/author/rights evidence required** |
| `docs/assets/ai-dashboard-hero.svg` | 2411 | `574a28620717f44a4938389f439a05c3d174f669` | **Unverified — human source/author/rights evidence required** |
| `docs/assets/category-agents.svg` | 1258 | `732f1c54fa3ecf480a57bf7bbef2a980b4e4c978` | **Unverified — human source/author/rights evidence required** |
| `docs/assets/category-build.svg` | 1258 | `02c368d1515370c0be89a362ecc54199544db496` | **Unverified — human source/author/rights evidence required** |
| `docs/assets/category-health.svg` | 1262 | `082ffb47185227ddf22184d5acd515da84e1a965` | **Unverified — human source/author/rights evidence required** |
| `docs/assets/category-reference.svg` | 1270 | `9207eaf74a9474960d2af00ef5566231d3d1e6c7` | **Unverified — human source/author/rights evidence required** |
| `docs/assets/category-start.svg` | 1258 | `0123a232e0e7af01c1aa1d761b364a3de8abda28` | **Unverified — human source/author/rights evidence required** |
| `docs/assets/category-trust.svg` | 1278 | `81b44041b4f2f7a980ef3e49af5e7366d800c828` | **Unverified — human source/author/rights evidence required** |
| `docs/assets/documentation-hero.svg` | 3671 | `d03aa3fe602b3b6ec25abde6f538579f9e63d227` | **Unverified — human source/author/rights evidence required** |
| `docs/assets/documentation-hub.svg` | 3471 | `c7f531b4605ea5bc249fdbd4443b08a5e05c4742` | **Unverified — human source/author/rights evidence required** |
| `docs/assets/healthqualify-home.svg` | 3312 | `7faad40f0f61d04536911e935e863b61b43638af` | **Unverified — human source/author/rights evidence required** |
| `docs/assets/social-preview.svg` | 1508 | `9e1a026b4010ad879de10005615d0ae776264d18` | **Unverified — human source/author/rights evidence required** |
| `docs/assets/visual-product-areas.svg` | 1857 | `bbc2d18b09f1c02b219dfe741f9e99968790e827` | **Unverified — human source/author/rights evidence required** |
| `website/public/brand-mark.svg` | 365 | `e1ebf91a267805361157aac4f8bbed48ffa026d1` | **Unverified — human source/author/rights evidence required** |
| `website/public/social-preview.svg` | 1707 | `3ab7ba50a3b41245baccb66a5d8b224443d02876` | **Unverified — human source/author/rights evidence required** |

Every file above requires individual authorship and license evidence. Avoid declaring any image independently authored merely because it is plain SVG without embedded media.

## Website source review

Reviewed the tracked `website/src/layouts/BaseLayout.astro`, `website/src/styles/site.css`, and these pages: index, qualification, agents, local-edition, community, demo, architecture, showcase. Searched for explicit third-party brand claims, font embedding, URL/image imports, and externally linked visual components.

**Observations:** HealthQualify text/branding is used; social-preview URL points to this project's own planned GitHub Pages path; link destinations mainly concern this repository. The CSS identifies a preferred Inter font but includes fallbacks and no bundled font or remote font URL. The CSS file previously contained an unsupported authorial/legal assertion of being “original MIT/Apache-compatible”; it is being replaced with a factual, non-certifying header.

**Not completed:** side-by-side comparison to competitor sites, trade dress/trademark clearance, ownership contracts/assignments, originality of the creative shapes, visual inspection of every rendered page, and review of generated CI screenshots/artifacts. No evidence of copying was established by these searches, but absence of references is not proof of originality.

## Dependency inventory — lockfile declarations

File: `website/package-lock.json`, lockfile version 3; 378 entries **including root**.

| License field as recorded in lockfile | Package entries |
|---|---:|
| `MIT` | 317 |
| `Apache-2.0` | 15 |
| `ISC` | 11 |
| `LGPL-3.0-or-later` | 10 |
| `BSD-2-Clause` | 9 |
| `Apache-2.0 AND LGPL-3.0-or-later` | 3 |
| `BSD-3-Clause` | 3 |
| `not declared` | 2 |
| `CC0-1.0` | 2 |
| `BlueOak-1.0.0` | 2 |
| `Apache-2.0 AND LGPL-3.0-or-later AND MIT` | 1 |
| `Python-2.0` | 1 |
| `0BSD` | 1 |
| `(MIT OR CC0-1.0)` | 1 |

**Investigation required:**
- `node_modules/zod-to-ts` version `1.2.0` has no `license` field in this lockfile. Check authoritative release package metadata and distributed license file rather than infer license from its peers.
- `@img/sharp-libvips-*` optional platform packages declare `LGPL-3.0-or-later`; related `@img/sharp-*` packages include combined license expressions. Review whether/how libvips or other native binaries are redistributed and comply with applicable obligations.
- Confirm exact installed/locked versions, platform-dependent optional packages, bundled notices and the actual contents of `website/dist` and developer binaries. The lockfile is not itself a verified SBOM, and a license identifier is not the text of a license.
- Review `requirements-docs.txt` (`mkdocs`, `mkdocs-material`) and `requirements-security.txt` (`cryptography`, `pydicom`) by producing fully resolved Python lock/SBOM from the shipping environment, then confirm all bundled licenses.
- Ollama and Qwen weights are optional separate downloads and should not be represented as redistributed by HealthQualify; if future bundles include them, conduct separate model/weight license reviews.

## Human sign-off checklist

- [ ] Name actual rights holders for each SVG and website page; obtain creation/assignment or third-party permission evidence
- [ ] Record independently generated SHA-256 for each shipped graphic and screenshot
- [ ] Complete side-by-side human design similarity/trade-dress review against any referenced inspiration and other relevant third-party UIs
- [ ] Review HealthQualify brand name/logo clearance and counsel advice where applicable
- [ ] Obtain resolved SBOM and inspect exact third-party license texts/notices including LGPL-related platform packages
- [ ] Verify source and license for any manually captured or CI-generated screenshot before publication
- [ ] Confirm no PHI, regulated customer UI, confidential reference art or employment-restricted IP was used
- [ ] Maintain required notices in source and any distributed binary/static artifact
- [ ] Independent owner/legal reviewer signs and dates launch gates in `docs/PUBLIC_LAUNCH_READINESS.md`

**Decision:** continue private developer-alpha evaluation; no public visibility switch, third-party IP clearance assertion, formal regulatory validation or distribution authorization.
