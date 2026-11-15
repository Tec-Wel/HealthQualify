# HealthQualify v0.4 — Security and Healthcare Interoperability Alpha

**Purpose:** Demonstrate security design controls and carefully scoped healthcare integration checks. Not production-ready, validated for regulated use, or suitable for PHI.

## Implemented controls

| Area | Engineering implementation | Unmet release gate |
|---|---|---|
| Identity | PBKDF2-HMAC-SHA256 passwords, random salts, 12+ character minimum, short-lived opaque hashed sessions, explicit logout | MFA/SSO, password recovery, lockout/rate limits, identity proofing, operational account lifecycle |
| Authorization | Deny-by-default admin / QA / validator / viewer actions; server derives user identity from session | Institution-specific role policy, multi-tenancy, per-system permissions, independent authorization testing |
| Review | Separate author/reviewer and fresh credential QA attestation tied to exact protocol digest | Independently validated Part 11 electronic signature, trustworthy time/identity, controlled SOPs |
| Evidence | AES-256-GCM file encryption; Ed25519 technical manifest signatures with externally held keys | KMS/HSM keys, access controls, immutable/WORM retention, backups, audit log integrity, legal validation |
| Audit | SQLite security/auth events, qualification events and reviewer actions | Tamper-resistant centralized audit log, time sync, monitoring and policy-controlled retention |
| Privacy | Synthetic-data-only workflows; no raw FHIR observations in assertion output | PHI data minimization, de-identification assurance, HIPAA/DPDP analysis, DPA/BAA, privacy threat review |
| FHIR | TLS verified HTTPS GET, exact preapproved origin, token from environment, no redirects, bounded response | Strong DNS egress filtering, auth interoperability profiles, OAuth2/SMART, real deployment approval |
| HL7 v2 | Bounded MLLP pack/unpack + segment metadata; no live network sessions | TLS/VPN, mutual auth, ACK workflow, implementation profiles and live staging tests |
| DICOM | Optional pydicom stop-before-pixels offline metadata inspection | DICOMweb/DIMSE C-ECHO/C-FIND/C-STORE, secure endpoints, validated image workflows |
| Equipment | Passive validated synthetic status snapshot | Vendor protocols, safe network adapters, calibration/witnessed IQ/OQ/PQ |
| Security testing | Unit/integration tests for RBAC, failed auth, URL gating, crypto tampering, synthetic inputs | Independent penetration test, SAST/DAST/SCA, threat model verification and recovery exercises |

The original unprotected local development API module remains present for legacy tests, but `python -m healthqualify.appcli serve` now uses the authenticated API. The old code is **not suitable for deployment**.

## Setup: authenticated single-site API

Python 3.12 recommended. The new crypto and DICOM utilities require:

```bash
python -m pip install -r requirements-security.txt
python -m unittest discover -s tests -v
python -m healthqualify.appcli --db /tmp/healthqualify-secure.db init

# Interactive password entry, no secret in shell history:
python -m healthqualify.appcli --db /tmp/healthqualify-secure.db bootstrap-admin admin_owner

# Local interface only. No port is published by Docker Compose.
python -m healthqualify.appcli --db /tmp/healthqualify-secure.db serve
```

Connect to **http://127.0.0.1:8877** (API, not a React UI). Authenticate using `POST /login` JSON `{"username":"admin_owner","password":"..."}`, then supply the short-lived bearer token on permitted API routes. Note HTTP is permitted **only on loopback**; do not run a public reverse proxy until TLS, origin protections, rate limiting, and external IAM are implemented.

API permission matrix:

| Role | Read | Draft protocols | Execute | Baseline | View audit | Manage users |
|---|---|---|---|---|---|---|
| admin | Yes | Yes | Yes | Yes | Yes | Yes |
| qa | Yes | No | No | Yes | Yes | No |
| validator | Yes | Yes | Yes | No | No | No |
| viewer | Yes | No | No | No | No | No |

Example (local only): `POST /users` accepts username/password/role, requires an admin bearer token. The dedicated `create-user` command requests an administrator's password interactively.

## Technical evidence encryption and signatures

Generate keys in a safe secret manager (the following local example creates fresh test-only keys):

```bash
export HEALTHQUALIFY_AES_KEY_B64="$(python -c 'import os,base64;print(base64.b64encode(os.urandom(32)).decode())')"
export HEALTHQUALIFY_SIGN_SEED_B64="$(python -c 'import os,base64;print(base64.b64encode(os.urandom(32)).decode())')"
python -m healthqualify.appcli protect-export /tmp/hq-report /tmp/hq-protected
```

Obtain the trusted Ed25519 public key from the signature receipt and verify it independently against a known trusted copy:

```bash
export HEALTHQUALIFY_PUBLIC_KEY_B64='<independently-trusted-public-key-base64>'
python -m healthqualify.appcli verify-protected /tmp/hq-protected
```

These tools **encrypt signed technical exports**. SQLite workspace content is not encrypted at rest by the application. Whole-disk encryption, KMS, sealed backup policies, audit history and controlled deployment are still required. Never store raw PHI or production secrets in the alpha database.

QA review attestation (not a regulated electronic signature):

```bash
python -m healthqualify.appcli --db /tmp/healthqualify-secure.db \
  review-attest qa_user <protocol-id> REVIEWED 'Engineering review of synthetic baseline'
```

The CLI prompts for a fresh password, checks QA permissions and author separation, and signs the exact protocol digest. The receipt does **not** satisfy Part 11 on its own.

## Healthcare integration use cases

### FHIR (read-only, approved HTTPS endpoint)

Requires an organization-authorized non-production FHIR endpoint, with an explicit origin and a token held outside Git:

```bash
export HEALTHQUALIFY_FHIR_ORIGIN='https://fhir-staging.example.org'
export HEALTHQUALIFY_FHIR_BEARER='<read-only-staging-token>'
python -m healthqualify.appcli fhir-check-approved \
  https://fhir-staging.example.org/fhir/Observation/123 \
  resourceType '"Observation"' --authorize-read-only
```

The host/path must exactly match the configured origin and `/fhir/` prefix. No redirects, writes, query strings or IP-literal/private addresses. **This is an assertion adapter, not a full FHIR conformance test suite.** DNS/egress must be independently secured and site authorization documented. Do not send production PHI.

### HL7 v2 MLLP
Use `healthqualify.hl7_mllp.pack_mllp`, `unpack_mllp`, and `analyze_message` for bounded synthetic payloads. No TCP sender, MLLP listener or ACK exchange is claimed. The CLI can inspect an already captured synthetic MLLP frame using `hl7-mllp-inspect <file> --authorize-synthetic`.

### DICOM
`dicom-synthetic <file> --authorize-synthetic` reads locally supplied synthetic DICOM metadata with pydicom and stops before pixel data; it does not transmit files to a PACS.

### Medical equipment
`device-snapshot <file> --authorize-synthetic` validates a passive, authorized synthetic telemetry object. It sends no commands.

## Stop/go gates for customer introduction

A healthcare organization must independently complete a threat model, secure deployment architecture and penetration testing, supported source-system/clinical integration qualification, privacy and data protection assessment, operating SOPs, backup and disaster recovery tests, clinical/intended-use acceptance criteria, and the applicability/validation of any regulated record or electronic-signature requirements. No "FDA-certified," "GMP compliant," or clinically validated claims should be made from passing this repository's tests.
