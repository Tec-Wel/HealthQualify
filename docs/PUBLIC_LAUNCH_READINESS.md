# Public open-source launch readiness — release decision gates

**Current disposition: HOLD FOR HUMAN REVIEW.** This checklist is not a compliance certificate, legal opinion, or release approval. The repository is currently intended as a private developer-alpha preparation environment; public visibility is changed only after independent authorization.

## Must pass before making repository public

| Gate | Technical deliverable | Human/independent evidence |
|---|---|---|
| License | Retain Apache-2.0, accurate attribution and third-party notices | Verify copyright owner, inventor/contributor rights, employment/contract obligations, and patent position |
| Owner / patents / trademarks | Document [owner and invention release decision](OWNER_IP_RELEASE_DECISION.md) and [trademark guidance](../TRADEMARK_POLICY.md) | Authorized owner and qualified IP counsel review before disclosure; do not commit privileged inventions or confidential contracts |
| Privacy | Accurate privacy notice and synthetic-only handling | Assess traffic, storage, deletion, data processing and public claims |
| Source and history | Full-history secrets / PHI / confidential-data scan | Human triage of findings, high-risk manual sampling, remove and rotate disclosed secrets if present |
| Dependencies and assets | Versioned license inventory + SBOM | Manual transitive dependency and bundled asset review, including model weights |
| Independent branding and design provenance | Original HealthQualify product positioning; no unnecessary third-party inspiration claims | Review website, screenshots, SVGs, logos, fonts, templates and source provenance against [design/IP checklist](INDEPENDENT_DESIGN_IP_REVIEW.md); preserve required attribution |
| Security | Private disclosure route, supported-scope statement, tests, vulnerability review | Set private vulnerability reporting in repository settings; resolve critical issues |
| Binaries | Platform build smoke tests, checksums and provenance | Native first-run UI tests, OS signing/notarization decision and separate bundle/license review |
| Governance | Contribution, conduct and support docs | Confirm a private community-conduct reporting contact/channel and DCO or alternative process |
| Claims | README / docs / distribution consistent with developer alpha | Regulatory/privacy/legal review of medical/quality/compliance language |
| Release | Versioned changelog, selected tag, release notes, verified assets | Authorized maintainer approval |
| Public switch | Publication of repo and approved release | Explicit owner sign-off **after** all gates |

## Work that remains manual

- Confirm legal rights, inventor and copyright positions; do not guess a rights holder. Maintain evidence and patent strategy privately outside the future public repository.
- Enforce DCO checks on new PR commits, and independently verify copyright/assignment rights for prior contributions; a DCO is not an ownership transfer.
- Inspect all **historical commits, branches, tags and hidden/deleted paths** for secrets, confidential code, patient/health data or employer-controlled material. Automated detection can miss undisclosed intellectual property. Remediate and rotate any compromised secrets **before publication**.
- Verify distribution license compatibility for optional Ollama/model weights and all packaged software. Qwen is **not bundled**.
- Complete the independent-branding and asset-provenance checklist; removing an inspiration phrase alone does not establish original design or IP clearance.
- Confirm a private vulnerability intake and confidential community-conduct contact (no addresses have been invented).
- Test the native UI and installers on Windows, macOS and Linux; GitHub Action help-text smoke tests are insufficient.
- Approve final README descriptions, disclaimers and regulated intended use with qualified reviewers.
- Decide publication visibility, final release tag and actual copyright owner only after review.

## How to review CI evidence

The GitHub workflow `.github/workflows/open-source-launch-audit.yml` can run repository licensing/SBOM, static secret checks and documentation gates. Its output is **preliminary technical evidence only**. Review findings and the release assessment; CI does not flip public visibility, publish releases, certify compliance or sign agreements.

## No-paid-services policy

The project remains free to run with no cloud account, purchased API tokens, paid hosted LLM, or required network connection for the deterministic core. Hardware, OS and optional externally selected infrastructure may cost money. Optional local Ollama/Qwen installation is separate, requires conscious opt-in, and incurs no vendor per-token hosted inference fee.

## Release record template

| Field | Entry |
|---|---|
| Commit and candidate tag | PENDING |
| Legal owner and counsel determination | PENDING |
| IP clearance and history-scan disposition | PENDING |
| SBOM and dependency licenses | PENDING |
| Model/visual asset rights | PENDING |
| Security assessment / private reporting confirmation | PENDING |
| OS UI installer acceptance | PENDING |
| Regulated-claim review | PENDING |
| Responsible publication approver and date | PENDING |
| Decision | **HOLD / NOT APPROVED FOR PUBLICATION** |

See [LICENSE](https://github.com/Tec-Wel/HealthQualify/blob/main/LICENSE), [NOTICE](https://github.com/Tec-Wel/HealthQualify/blob/main/NOTICE), [THIRD_PARTY_NOTICES.md](https://github.com/Tec-Wel/HealthQualify/blob/main/THIRD_PARTY_NOTICES.md), [PRIVACY.md](https://github.com/Tec-Wel/HealthQualify/blob/main/PRIVACY.md), [DISCLAIMER.md](https://github.com/Tec-Wel/HealthQualify/blob/main/DISCLAIMER.md), and [SECURITY.md](https://github.com/Tec-Wel/HealthQualify/blob/main/SECURITY.md).
