# Third-party dependencies, models and assets — license review register

**Status: preliminary; not a complete legal inventory.** Verify resolved package versions, all transitive dependencies, distribution artifacts, and actual licenses from original upstream sources before publishing binaries.

| Component / area | Use | License action required before redistribution |
|---|---|---|
| Python standard library | Core offline runner and local web application | Python version and PSF license notice where applicable |
| `cryptography` (optional) | Protected export/security demonstrations | Confirm installed version, Apache-2.0/BSD licensing and bundled cryptographic dependencies |
| `pydicom` (optional) | DICOM metadata demonstrations | Confirm installed version and its licensing |
| `Astro` and Node.js website dependencies | Static product website | Confirm resolved package versions, transitive licenses and redistributed assets; review `website/package-lock.json` |
| `mkdocs` | Documentation build | Confirm release license and transitive packages |
| `mkdocs-material` | Documentation theme | Confirm exact license and any included fonts/assets; optional paid offerings are not required |
| `PyInstaller` | Development OS binaries | Check PyInstaller license, bootloader exception, embedded dependencies and distribution obligations |
| `Ollama` | Optional *separately installed* local inference server | Confirm its own license and user-installation terms; not bundled by default |
| Qwen model `qwen3:8b` | Optional *separately downloaded* weights | Verify exact weights, Ollama tag/digest, authoritative model license and attribution **before** distributing any model weights; weights are not bundled in HealthQualify |
| SVGs, screenshots and logos | Documentation and UI | Record per-file authorship and origin for `website/public/`, `website/src/` and `docs/assets/`; confirm permissions and licenses, including screenshots and embedded graphics |
| Healthcare formats / regulatory text | Synthetic examples and reference summaries | Confirm that third-party schemas, HL7/DICOM/standards content and regulatory texts are lawfully reusable; do not redistribute paywalled standards |

**Do not infer that Apache-2.0 on the repository relicenses third-party software or model weights.** Model availability and lack of per-token fees do not establish redistribution rights.

## Automated evidence

The launch-check workflow produces an SPDX SBOM for checked-out repository files and a Python distribution license report for the *CI environment*. Neither alone establishes completeness for packaged binaries, separately installed models or external content. See [public launch checklist](docs/PUBLIC_LAUNCH_READINESS.md) for required human verification.

## Release sign-off fields (to be completed by responsible maintainers)

- Copyright owner and authorization: **PENDING HUMAN REVIEW**
- Third-party source origin and license compatibility: **PENDING HUMAN REVIEW**
- Model-weight licensing and packaging decisions: **PENDING HUMAN REVIEW**
- Documentation art and font provenance: **PENDING HUMAN REVIEW**
- Installer dependency obligations: **PENDING HUMAN REVIEW**

The absence of a completed sign-off **blocks public-launch readiness**, not ordinary synthetic developer testing. Product copy must not imply affiliation with or endorsement by another healthcare platform. **Do not remove any attribution actually required by a dependency's or asset's license** simply to avoid naming external organizations. See [the independent-branding and IP review](docs/INDEPENDENT_DESIGN_IP_REVIEW.md).
