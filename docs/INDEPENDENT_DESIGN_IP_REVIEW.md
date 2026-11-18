# HealthQualify — independent branding and design/IP review

**Status: OPEN — human legal, design and ownership review required before any public launch.** This checklist is an internal technical inventory aid, not a legal opinion, proof of independent creation, trademark clearance or third-party-license audit.

## Product identity policy

- Describe HealthQualify using its own positioning: **local-first software qualification, reproducible synthetic testing, evidence traceability and advisory investigations**.
- Do not describe product screens, brand graphics or the website as "inspired by", "based on", "a clone of", or "like" a named third-party website in public-facing copy.
- Do not use third-party trademarks, logos, screenshots, artworks or distinctive brand elements as decoration or as a suggestion of affiliation or endorsement.
- **Keep truthful and legally required attribution**. The Apache-2.0 LICENSE, NOTICE, THIRD_PARTY_NOTICES.md, library/model/component notices, copyright statements and applicable standards references must not be silently erased. Links necessary to identify licensing sources, external specifications or security notices are not marketing endorsements.
- Preserve factual product and technical documentation; no need to suppress legitimate mentions of FDA regulations or standards bodies where accuracy requires them.
- Apply these rules to future website copy, screenshots, pull-request titles and commit messages. Do not rewrite historical commits merely to remove a descriptive phrase; escalate any actual protected-content, secret or unauthorized-IP concern separately.

## Current-text findings (current default-branch search, 2026-11-18)

| Surface | Finding | Action |
|---|---|---|
| `README.md` | Called the Astro landing page "MONAI-inspired" | Replaced with HealthQualify's independent branding description |
| `website/README.md` | Included a competitor inspiration label and comparison | Replaced with original-product positioning and provenance review requirement |
| `THIRD_PARTY_NOTICES.md` | Preliminary license register | Retained and expanded Astro/Node and design-asset diligence |
| `NOTICE` and `LICENSE` | Ownership caveat and Apache-2.0 text | Preserved without substantive change |
| `website/src/layouts/BaseLayout.astro` | HealthQualify branding and first-party navigation | No named competitor branding seen in reviewed file |
| `website/package.json` | Astro development dependency | Track transitive licenses from lockfile and build outputs |

These are targeted source reviews, **not a verified exhaustive inventory**. Repository-wide indexed search can miss binary assets, deleted files, old commits, unindexed code, generated bundles and contextual resemblance. No visual similarity audit or ownership clearance has been completed.

## Mandatory design and asset provenance review

Maintainers must document for **every distributed** asset, template or significant design fragment (including `website/public/`, `website/src/`, `docs/assets/`, screenshots, social previews and build artifacts):

| Field | Required record |
|---|---|
| File/path and SHA-256 | Exact asset and version |
| Creator and source | Who created it, evidence of origin and the upstream URL if applicable |
| Rights basis | Owned original work, properly assigned contributor work, compatible third-party license, or documented permission |
| License / notice obligations | Exact text and location of attribution, NOTICE, license files and any restrictions |
| Use and redistribution | Whether bundled, modified, published or downloaded separately |
| Human reviewer and date | Decision, evidence link, and unresolved risks |

**No source or license should be invented.** If provenance cannot be established, place publication of the asset on hold, replace it with a verified original, or obtain legal permission.

## Release gates — all remain pending until evidenced

- [ ] Verify ownership/assignment and employer/contract obligations for contributed code and graphics
- [ ] Review all Astro pages for copied text, page composition, distinctive trade dress, icons, fonts and media
- [ ] Review brand name and logo for trademark conflicts with counsel where appropriate
- [ ] Inspect SVG and image files directly, not merely their filenames or Markdown references
- [ ] Inventory website lockfile dependencies, docs theme and bundled font/icon licenses
- [ ] Verify screenshot origin: genuine synthetic HealthQualify state, no third-party app UI or PHI
- [ ] Perform full Git history, branches and release-artifact review for secrets, sensitive data and potentially unauthorized IP
- [ ] Preserve required credits and license texts in all relevant distribution formats
- [ ] Have authorized owner/legal reviewer sign off before publishing repo, binary releases or website

## Practical controls for contributors

1. Use independent HealthQualify copy and creative assets. If a reference website was consulted, do not transplant its expressive design or source.
2. Explain asset provenance in PRs with paths and license evidence.
3. Treat npm, Python, fonts, optional model weights and external standards as separately licensed materials. Open-source software being free does not make all redistribution unrestricted.
4. Keep the repository private and publication workflows gated until `docs/PUBLIC_LAUNCH_READINESS.md` is signed off.

This review does **not** modify historical Git commits, delete a legal notice, change repository visibility, or authorize distribution.
