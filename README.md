# HealthQualify

**Open-source healthcare software validation and continuous qualification.**

> From approved requirements to executable tests, verifiable evidence, human review, and release-aware requalification — without an AI dependency.

**Status: pre-alpha foundation.** The initial CLI is a deterministic, synthetic-data demonstration. It is **not** a qualified system, a compliance certification, or a substitute for an organization's quality management system.

## What HealthQualify will do

HealthQualify combines the *capability categories* of regulatory guidance, qualification planning, IQ/OQ/PQ protocol generation, requirements traceability and gap analysis with a cloud-neutral execution and evidence engine.

1. **Understand** — system registry, intended use, regulatory applicability, versioned source references, GAMP-style risk planning and CSA profiles.
2. **Design** — approved requirements, URS/FRS, risk analysis, IQ/OQ/PQ protocols and manual procedures.
3. **Execute** — deterministic test adapters for configuration, REST/FHIR/HL7, SQL, software workflows and selected PQ scenarios.
4. **Prove** — results with distinct PASS, FAIL, ERROR, and NOT_RUN states; SHA-256 evidence manifest; requirements-to-execution traceability.
5. **Review** — deviations, CAPA links, controlled baselines, reviewer decisions and exports.
6. **Requalify** — change-impact mapping, release-related test recommendations, regulatory-change review and repeatable verification.

Optional AI assistants may draft requirements and protocols or explain failed tests, but cannot approve protocols or write authoritative PASS/FAIL results.

## First usable developer experience

Python 3.10+ and no external packages are required for the initial CLI:

```bash
python -m healthqualify.cli run examples/synthetic_lis/protocol.json --out .healthqualify/run
python -m healthqualify.cli verify .healthqualify/run
python -m unittest discover -s tests -v
```

The bundled synthetic LIS protocol contains deliberately failing checks, demonstrating that failures cannot be silently promoted to success. Exit codes: 0 = checks passed; 1 = failed/incomplete; 2 = malformed input or execution error.

## New: v0.2 healthcare qualification (feature branch)

Run the seven-case synthetic HL7/FHIR laboratory profile using the independent, no-AI engine:

```bash
python -m healthqualify.cli validate-v2 examples/synthetic_lis_v2/protocol.json
python -m healthqualify.cli run-v2 examples/synthetic_lis_v2/protocol.json --out .healthqualify/v2-run
python -m healthqualify.cli verify-v2 .healthqualify/v2-run
```

The demonstration intentionally reports **5 FAIL and 2 PASS**, so `run-v2` exits 1. It detects synthetic patient-ID mismatch, unit mismatch, missing critical notification, unauthorized cross-tenant access, and missing audit events. These assertions operate on **embedded synthetic fixtures**, not a live HL7 network or production healthcare environment.

`run-v2` prints the SHA-256 of its manifest. Save this digest outside the exported bundle, then pass it to `verify-v2 --trusted-manifest-sha256 <digest>` to identify substituted manifests. This is an integrity demonstration, not a signed/immutable evidence system.

Each v0.2 requirement declares a risk and acceptance basis. The CLI accepts draft protocols only: it cannot implement regulated approvals. A requirement without a linked executed test is reported as UNCOVERED / NOT_RUN rather than PASS.

See [healthcare foundation instructions](docs/HEALTHCARE_V02.md).

## Scope and boundaries

- **Target:** healthcare software, LIS/LIMS/EHR integrations, hospital IT, controlled software interfaces and eventually healthcare AI and equipment-connected systems.
- **Assurance methods:** IQ/OQ/PQ where justified; optional risk-based computer software assurance. Do not force IQ/OQ/PQ on every healthcare application.
- **Healthcare adapters:** HL7, FHIR, DICOM, equipment gateways and live environment inspection are *planned*, not implemented by this starter.
- **Evidence:** the starter records protocol bytes, test outcomes and hashes. Hashes detect changes relative to a trusted reference; they are not immutable storage, independent timestamps, Part 11 compliance, or valid electronic signatures.
- **Security:** synthetic data only in the example. Do not run against production systems or ingest PHI.
- **Regulatory:** site-specific applicability assessment and qualified human decisions are required. No automatic FDA/GMP certification.

## Architecture and roadmap

- [Product specification](docs/PRODUCT.md)
- [Architecture and security boundaries](docs/ARCHITECTURE.md)
- [Roadmap and benchmark](docs/ROADMAP.md)

**Core technology:** Python, local filesystem/SQLite (planned), later FastAPI, React, PostgreSQL and Docker. The same containers should run on EC2, GCP Compute Engine, Azure VMs or on-premises. Local SLM/LLM and hosted AI integrations remain opt-in.

## Inspirations and differentiation

- [ParaQualis GxP](https://github.com/paraqualis/paraqualis-gxp) — regulatory assistance, draft qualification packages, executable scripts and Claude Code workflows (MIT). HealthQualify is a separately developed **execution and evidence lifecycle** platform.
- [medtest-traceability](https://github.com/INNERLUXES/medtest-traceability) — requirement-to-test coverage and CI gaps (MIT). HealthQualify targets requirement-to-**executed-evidence** traceability.
- Other established test frameworks (pytest, Playwright, Locust, Inferno, etc.) should be integrated rather than rewritten.

Do not copy third-party code or regulated standards text without reviewing licenses and attribution.

## Open source

New HealthQualify code: Apache-2.0. See [LICENSE](LICENSE).
Contributions and security reporting guidance will expand as the foundation matures.
