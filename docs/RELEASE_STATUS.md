# HealthQualify — implementation status (v0.4 security/interoperability alpha)

**v0.4 additions:** PBKDF2 identity, role-gated short-lived sessions, authenticated local API, technical QA review attestations, AES-256-GCM encrypted exports, Ed25519 integrity signatures, opt-in approved-origin HTTPS FHIR checks, bounded MLLP framing, offline DICOM metadata and passive device snapshot inspections, minimized persisted observations, and fail-closed regulated release gates. See [Security & Interoperability v0.4](SECURITY_INTEROP_V04.md). **Important:** This release is not a complete regulated-production platform. All features below are independently authored HealthQualify proof-of-concepts and developer tools. Do not use on PHI or for a regulated approval decision.

| Requested module | Built now | Still required for production |
|---|---|---|
| Regulatory Studio | Source-linked framework catalog, explicit applicability, offline text diffs, operator-supplied snapshots, optional eCFR section fetch | Official change ingestion scheduler, legal review workflows, regulatory source verification and licensed content handling |
| Requirements Studio | Draft URS and risk/assurance planning functions | Document import, review UX, true human-controlled approval and requirement revision history |
| Protocol Studio | Versioned draft v0.2 JSON protocols in SQLite, baseline event and author/reviewer separation | Signed approval, stronger schema, versioned executable test definitions, independent trusted record store |
| Healthcare Integration | Opt-in staging HTTPS FHIR GET, MLLP framing, offline synthetic DICOM metadata, passive equipment snapshot | Production HL7/MLLP transport, full FHIR/DICOM interoperability, live equipment integrations, data governance, clinical qualification |
| DeviationFlow | Persistent findings from runs, retest-linked resolution requirement, audit event | Investigator/owner assignment, CAPA workflows, multifactor identity, supervisory review |
| Evidence Vault | JSON/HTML export; SHA-256/HMAC plus optional AES-GCM encrypted Ed25519-signed technical archives; QA reauthentication receipt | Independent trusted time, HSM/KMS, protected operational storage, backup/restore, retention and validated regulated e-signatures |
| Dashboard/API | Authenticated local HTTP API with admin/QA/validator/viewer permissions; former dashboard is legacy and no longer default | React UX, FastAPI, multi-tenant isolation, MFA/SSO, rate limits, TLS, threat-model testing |
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
- HealthQualify code is independently developed; third-party license obligations must be reviewed before reusing external code.
- No copyrighted GAMP 5 text is redistributed.
- Every authoritative qualification decision is human-controlled under a separately established quality process.
- Hashes and shared-secret receipts do not alone create immutable regulated records.
- Regulatory applicability depends on actual jurisdiction and intended use.
- Cloud portability of the container does not mean secure cloud production readiness.
