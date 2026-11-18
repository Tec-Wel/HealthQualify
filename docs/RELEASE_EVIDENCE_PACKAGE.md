# HealthQualify — prepublication evidence package

**HOLD — NOT AUTHORIZED FOR PUBLIC RELEASE.** This document is a reusable release evidence index, not an approval or a legal opinion. Keep sensitive evidence and attorney communications **outside** any repository that may become public.

## Current verified technical observations (2026-11-18)

- The repository's `LICENSE` contains Apache-2.0, and `NOTICE` states that the legal copyright holder is pending verification.
- The repository is private; the default branch is protected by a ruleset requiring pull requests, `unit` and `Verify Signed-off-by trailers` CI contexts.
- A tracked-asset and package metadata inventory exists at [VISUAL_ASSET_DEPENDENCY_AUDIT.md](VISUAL_ASSET_DEPENDENCY_AUDIT.md). The record does **not** verify visual originality.
- Optional Ollama and Qwen model weights are independently installed and **not authorized for redistribution by the repository's Apache license**.
- No official GitHub Release asset was found in the checked release list at the time this document was prepared.
- The three Dependabot major-version PRs remain open with prior DCO check failures. Rerunning those old PR checks did not load the newly updated DCO bot exception. Do not waive mandatory checks or claim these upgrades approved.
- The remaining old feature branch's primary qualification/benchmark files exist in `main`; differences and history still require separate review before deletion.

## Produce and retain immutable technical evidence

From a reviewed local clone:

```sh
python scripts/create_provenance_manifest.py --output healthqualify-provenance-review.json
python -m unittest discover -s tests -q
```

Store the generated JSON outside the future published repository along with the exact commit SHA and review timestamp. The script records tracked asset and dependency declaration SHA-256 values, **not** license authorship or permissions. Prefer generating final evidence on a clean checkout and compare with the actual packaged website/build output.

## Dependency-license research — preliminary, not redistribution clearance

- `zod-to-ts` is listed in the website lockfile without a license field. Public package metadata indicates an MIT license for the package family; verify the **exact pinned v1.2.0 distribution's LICENSE text** and record the verified evidence before asserting a final license.
- `@img/sharp-libvips-*` native optional packages declare LGPL-3.0-or-later obligations. Confirm whether the final released website, installer, container or other binaries **actually contain** these components, and if so include the correct LGPL notices, source/relinking information and other applicable obligations. A static Astro site does not automatically redistribute every npm build dependency.
- Do not redistribute Ollama or Qwen weights by default; optional local download remains the separate operator's choice and must be evaluated against the exact upstream model license if the project ever changes its packaging.

These findings are dependency-diligence leads, **not a complete license audit**, an Apache relicensing of dependencies or permission to publish.

## Owner / patent / legal review (all PENDING)

| Decision | Required evidence / sign-off |
|---|---|
| Copyright owner, code and artwork assignments | Legal name, authority and chain of title verified privately |
| Inventions, prior disclosures and patent position | Qualified patent counsel's release-before-disclosure determination, retained privately |
| Trademark and artwork | Clearance, asset creator/origin review, approved brand policy |
| Dependency compatibility | Resolved version and transitive license inventory; notices in actual bundles |
| Optional model weights | Exact model version/digest, upstream license; no default redistribution |
| Technical license/security history | Secret/PHI/confidential-content review across reachable branches, refs and history; all findings disposed |
| Regulatory/intended-use statements | Human review of synthetic-only alpha boundaries and no unsupported FDA validation claims |

## Security and disclosure intake

The SECURITY.md policy intentionally describes the private GitHub advisory mechanism only **if enabled**. GitHub's private vulnerability *reporting* feature generally serves public repositories; do not claim it is enabled for the current private repository without confirming in GitHub Settings. An interim confidential owner-controlled contact remains **PENDING**. The optional `.github/VULNERABILITY_REPORT.yml` configures a form if the feature is available; it does not enable GitHub settings automatically.

## Required staged release workflow

1. Preserve an immutable source tree and commit/tag identity and test results.
2. Inventory every source, website, docs and installer artifact for hashes, bundled components, licenses and rights.
3. Confirm clean-room/synthetic examples only; separate retained internal security findings from public notes.
4. Smoke-test actual supported-platform installers and verify checksums; decide signing/notarization with appropriate ownership.
5. Prepare accurate CHANGELOG/release notes, supported environments, known limitations and a nonclinical disclaimer.
6. Record owner, qualified IP/legal, security and regulatory reviews in a restricted location.
7. Obtain explicit authorization for the exact public repository commit, tag, and assets **before** changing visibility or publishing distributions.

## Release decision

| Record | Status |
|---|---|
| Release candidate SHA/tag | PENDING |
| Provenance manifest and complete package SBOM | PENDING |
| Full-history sensitive-content disposition | PENDING |
| Owner, patent, trademark and third-party rights | PENDING |
| Installer smoke tests and verified checksums | PENDING |
| Confidential reporting channel | PENDING |
| Authorized release approver/date | PENDING |
| **Public release decision** | **HOLD** |

See [PUBLIC_LAUNCH_READINESS.md](PUBLIC_LAUNCH_READINESS.md), [OWNER_IP_RELEASE_DECISION.md](OWNER_IP_RELEASE_DECISION.md), and [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).
