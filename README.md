# HealthQualify

**Open-source healthcare software validation and continuous qualification.**

> From approved requirements to executable tests, verifiable evidence, human review, and release-aware requalification — without an AI dependency.

**Status: v0.5 developer alpha — continued qualification and evidence hardening (not production validated).** The initial CLI is a deterministic, synthetic-data demonstration. It is **not** a qualified system, a compliance certification, or a substitute for an organization's quality management system.

## What HealthQualify will do

HealthQualify combines the *capability categories* of regulatory guidance, qualification planning, IQ/OQ/PQ protocol generation, requirements traceability and gap analysis with a cloud-neutral execution and evidence engine.

1. **Understand** — system registry, intended use, regulatory applicability, versioned source references, GAMP-style risk planning and CSA profiles.
2. **Design** — approved requirements, URS/FRS, risk analysis, IQ/OQ/PQ protocols and manual procedures.
3. **Execute** — deterministic test adapters for configuration, REST/FHIR/HL7, SQL, software workflows and selected PQ scenarios.
4. **Prove** — results with distinct PASS, FAIL, ERROR, and NOT_RUN states; SHA-256 evidence manifest; requirements-to-execution traceability.
5. **Review** — deviations, CAPA links, controlled baselines, reviewer decisions and exports.
6. **Requalify** — change-impact mapping, release-related test recommendations, regulatory-change review and repeatable verification.

Optional AI assistants may draft requirements and protocols or explain failed tests, but cannot approve protocols or write authoritative PASS/FAIL results.

## v0.5 Backlog convergence

**[Read the v0.5 implementation and nine-issue matrix](docs/V05_BACKLOG_CONVERGENCE.md).** New independent tools provide an offline-only strict v0.3 protocol, acceptance-source registry, conservative source-to-test impact analysis, versioned engineering evidence manifests, controlled CAPA investigation and retest, explicit risk-based CSA/IQ-OQ-PQ draft profiles, optional AI-provider abstraction, consistent SQLite backup/restore integrity checks, and an internal benchmark harness.

```bash
python -m unittest discover -s tests -v
python -m healthqualify.v05cli run examples/synthetic_lis_v3/protocol.json --out .healthqualify/v05-run
python -m healthqualify.v05cli impact examples/synthetic_lis_v3/protocol.json healthqualify/healthcare.py
```

The example deliberately reports five failures. The run returning status 1 is expected. **This is not a regulated qualification approval.**

### Git branch hygiene

The three old feature branches are already merged via PRs #10-12. A guarded main-branch cleanup workflow checks merged PRs and exact original branch SHAs before attempting deletion after a successful test run. It never touches `main`. See [branch cleanup controls](docs/V05_BACKLOG_CONVERGENCE.md#branch-cleanup-policy).

## Security and interoperability alpha: v0.4

**[Security and healthcare interoperability guide](docs/SECURITY_INTEROP_V04.md)** provides the authenticated API, approved test-environment connections, cryptographic evidence export and regulated release gates.

```bash
python -m pip install -r requirements-security.txt
python -m unittest discover -s tests -v
python -m healthqualify.appcli --db /tmp/hq-secure.db init
python -m healthqualify.appcli --db /tmp/hq-secure.db bootstrap-admin admin_owner
python -m healthqualify.appcli --db /tmp/hq-secure.db serve
# Local authenticated API: http://127.0.0.1:8877
```

The new secure API is loopback-only, requires login and enforces admin/QA/validator/viewer roles. The former v0.3 development API is legacy code and **not** the default runtime. The Docker Compose configuration does not publish an HTTP port.

FHIR staging checks support explicitly approved HTTPS read-only access. HL7/MLLP supports bounded offline transport framing, DICOM supports local synthetic metadata inspection, and equipment integration currently supports passive synthetic telemetry. Full clinical interoperability still requires site-specific integration and qualification.

Encrypted technical evidence archives use AES-256-GCM and Ed25519 receipts with externally managed keys; these **are not validated electronic signatures**. The customer-release gate is intentionally blocked:

```bash
python -m healthqualify.appcli readiness
```

Release readiness requires operational security, privacy, clinical integration, assurance and independent regulatory review. No PHI should be supplied.

## Local product alpha: v0.3

The existing v0.1 and v0.2 synthetic engines remain available. The new workspace CLI connects the product modules behind a SQLite-backed local development workflow:

```bash
python -m unittest discover -s tests -v
python -m healthqualify.appcli --db healthqualify.db init
python -m healthqualify.appcli --db healthqualify.db system-add "LIS Demo" "Synthetic lab interoperability" "Engineer"
python -m healthqualify.appcli frameworks
python -m healthqualify.appcli agents
```

See **[v0.3 Product and Developer Guide](docs/PLATFORM_V03.md)** for the complete draft-protocol → baseline review → execution → deviations → evidence-report workflow, local dashboard and restricted REST API. The developer baseline is not a Part 11 electronic signature. Actual live HL7/FHIR integration testing and clinical use are **not** enabled.

Supported v0.3 concepts:

- **System Registry** — SQLite systems, intended use, owners
- **Requirements / Risk Studio** — URS drafts and proportional assurance-plan suggestions
- **Protocol Studio** — stored versioned v0.2 synthetic protocols, separate author/reviewer baseline events
- **Qualification Runner** — deterministic IQ/OQ/PQ fixture assertions and findings
- **Evidence Vault** — HTML/JSON report export, hashes, opt-in HMAC receipt
- **DeviationFlow** — recorded findings, evidence-linked retest requirement for resolution
- **Regulatory Studio / RegWatch** — source-linked catalog, explicit applicability decisions, operator-supplied text comparisons and snapshots
- **Continuous Qualification** — conservative protocol-to-protocol impact review via `review-v2`
- **ModelQual** — offline metrics on supplied prediction sets
- **Optional AI** — opt-in local Ollama draft assistants; never authoritative
- **Dashboard / API** — local-only HTML dashboard and bearer-token-gated write endpoints
- **Container** — local Docker Compose profile, bound to localhost only

### Local dashboard

```bash
export HEALTHQUALIFY_API_TOKEN="$(python -c 'import secrets;print(secrets.token_urlsafe(32))')"
python -m healthqualify.appcli --db healthqualify.db serve
# Visit http://127.0.0.1:8765
```

The portable image can be deployed on EC2/GCP/Azure/on-prem after appropriate security engineering; the provided Compose file is for local development only. No PHI, regulated production connection, protected audit trail or legal qualification approval is supported.

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

## Engineering approach

- Other established test frameworks (pytest, Playwright, Locust, Inferno, etc.) should be integrated rather than rewritten.

Do not copy third-party code or regulated standards text without reviewing licenses and attribution.

## Open source

New HealthQualify code: Apache-2.0. See [LICENSE](LICENSE).
Contributions and security reporting guidance will expand as the foundation matures.
