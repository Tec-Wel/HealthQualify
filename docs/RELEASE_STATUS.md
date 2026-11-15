# HealthQualify — actual implementation status (v0.3 developer alpha)

**Important:** This release is not a complete regulated-production platform. All features below are independently authored HealthQualify proof-of-concepts and developer tools. Do not use on PHI or for a regulated approval decision.

| Requested module | Built now | Still required for production |
|---|---|---|
| Regulatory Studio | Source-linked framework catalog, explicit applicability, offline text diffs, operator-supplied snapshots, optional eCFR section fetch | Official change ingestion scheduler, legal review workflows, regulatory source verification and licensed content handling |
| Requirements Studio | Draft URS and risk/assurance planning functions | Document import, review UX, true human-controlled approval and requirement revision history |
| Protocol Studio | Versioned draft v0.2 JSON protocols in SQLite, baseline event and author/reviewer separation | Signed approval, stronger schema, versioned executable test definitions, independent trusted record store |
| Healthcare Integration | Synthetic HL7/FHIR field assertions, restricted loopback-only read-only FHIR HTTP test | Real HL7/MLLP, authenticated FHIR, DICOM and vendor equipment interfaces with environment authorization and PHI governance |
| DeviationFlow | Persistent findings from runs, retest-linked resolution requirement, audit event | Investigator/owner assignment, CAPA workflows, multifactor identity, supervisory review |
| Evidence Vault | JSON/HTML export, SHA-256 manifests and optional HMAC receipt | Independently timestamped signatures, protected storage, backup/restore, configurable retention, e-signature assessment |
| Dashboard/API | Local server-side HTML and limited bearer-protected write API | React UX, FastAPI application, RBAC, multi-tenant isolation, TLS, threat-model testing |
| Cloud Deployment | One Dockerfile and local-only Compose demonstration | Secure production deploy manifests, PostgreSQL/object storage, tested AWS/GCP/Azure/on-prem templates |
| AI Assistance | Explicitly enabled local Ollama draft agents; offline model scoring | External provider governance, prompt injection defenses, document workflows, benchmarked model evaluations |
| Continuous Qualification | Conservative protocol-version diff and recommended test IDs | GitHub webhook integration, code component graph, documented release approvals and selective automatic reruns |

## Smoke tests

```bash
python -m unittest discover -s tests -v
python -m healthqualify.appcli --db /tmp/hq-demo.db init
python -m healthqualify.appcli frameworks
python -m healthqualify.appcli agents
python -m healthqualify.cli validate-v2 examples/synthetic_lis_v2/protocol.json
```

Synthetic protocol runs intentionally surface five defects; this is expected and does not mean the software's CI tests failed.

## Local FHIR demo connector

```bash
python -m healthqualify.appcli fhir-check-local \
  http://127.0.0.1:8000/fhir/Observation/1 resourceType '"Observation"' --allow-local-http
```

This succeeds **only if** you have independently started a synthetic FHIR fixture endpoint on localhost:8000 with that resource. The built-in unit test uses a mocked endpoint and does not contact the network. The connector never permits arbitrary remote hosts.

## Integrity receipt

```bash
export HEALTHQUALIFY_EVIDENCE_KEY="$(python -c 'import secrets;print(secrets.token_urlsafe(48))')"
python -m healthqualify.appcli seal /tmp/hq-report
python -m healthqualify.appcli verify-seal /tmp/hq-report
```

Keep the key external to the report directory. This verifies against a shared secret; it is **not** a digital signature, Part 11 electronic signature, or proof of regulatory approval.

## Development and compliance boundaries
- No code from ParaQualis was copied; its MIT repository supplied product inspiration only.
- No copyrighted GAMP 5 text is redistributed.
- Every authoritative qualification decision is human-controlled under a separately established quality process.
- Hashes and shared-secret receipts do not alone create immutable regulated records.
- Regulatory applicability depends on actual jurisdiction and intended use.
- Cloud portability of the container does not mean secure cloud production readiness.
