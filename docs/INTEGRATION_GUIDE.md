![Build & extend documentation](assets/category-build.svg)

[← **Documentation home**](README.md) &nbsp; / &nbsp; **Build & extend**

# Integration guide: supported boundaries and safe test connections

> **What you'll learn:** Use bounded localhost REST, read-only FHIR staging, and offline interoperability prototypes safely.

**On this page:** [1. Authenticated loopback workspace API](#1-authenticated-loopback-workspace-api) · [2. Standalone local JSON REST assertion](#2-standalone-local-json-rest-assertion) · [3. Read-only HTTPS FHIR staging assertion](#3-read-only-https-fhir-staging-assertion) · [4. HL7 v2, DICOM and equipment](#4-hl7-v2-dicom-and-equipment)

---


HealthQualify is designed to be cloud-neutral, but the current repository is **not** a production healthcare integration gateway. Integration demos require **synthetic data, authorized staging endpoints, and explicit opt-in flags**.

## 1. Authenticated loopback workspace API

Initialize a workspace and bootstrap the first administrator:

```bash
python -m healthqualify.appcli --db healthqualify.db init
python -m healthqualify.appcli --db healthqualify.db bootstrap-admin admin_owner
python -m healthqualify.appcli --db healthqualify.db serve
```

The interactive bootstrap asks for a password. The service defaults to `http://127.0.0.1:8877`, and `GET /health` is an unauthenticated health probe. A non-sensitive authenticated flow uses:

```bash
curl -X POST http://127.0.0.1:8877/login -H 'Content-Type: application/json' -d '{"username":"admin_owner","password":"YOUR_LOCAL_TEST_PASSWORD"}'
```

Copy the `access_token` response privately, then:

```bash
curl http://127.0.0.1:8877/systems -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

Use this *only on your own workstation*. Avoid real password literals in shared shell histories; use interactive secure clients where possible.

**Current routes:** unauthenticated `GET /health`; `POST /login`, `POST /logout`, `POST /users`, `POST /systems`, `POST /protocols`, `POST /baselines`, `POST /runs`; authenticated `GET /frameworks`, `/audit`, `/systems`, `/protocols`, `/runs`, `/deviations`.

Role policy includes `admin`, `qa`, `validator`, `viewer`. A session lasts roughly one hour. This is not hardened public infrastructure; it lacks MFA/SSO, TLS deployment, production rate limiting and tenant isolation.

## 2. Standalone local JSON REST assertion

The v0.5 `rest-check-local` checks a field of a synthetic JSON response from a loopback service. It **does not** execute an entire v0.3 protocol over HTTP or talk to arbitrary external hosts.

```bash
python -m healthqualify.v05cli rest-check-local http://127.0.0.1:8000/test/example status '"ready"' --authorize-synthetic
```

Start a synthetic local server separately; no server is bundled for that illustrative endpoint. The check is **GET-only**, bounded, loopback-only, limited to `/test/` paths, redacts observed values, and has no redirect following. Errors are not evidence of remote system failure without understanding environment configuration.

## 3. Read-only HTTPS FHIR staging assertion

Configure an approved staging origin and token outside Git:

```bash
export HEALTHQUALIFY_FHIR_ORIGIN='https://fhir-staging.example.org'
export HEALTHQUALIFY_FHIR_BEARER='YOUR_APPROVED_READ_ONLY_TOKEN'
python -m healthqualify.appcli fhir-check-approved https://fhir-staging.example.org/fhir/Observation/123 resourceType '"Observation"' --authorize-read-only
```

Replace placeholders with your **authorized non-production, synthetic-only** service. This is a field-level GET assertion, not a SMART-on-FHIR or full FHIR profile validation suite. No redirects, arbitrary query strings or production PHI.

## 4. HL7 v2, DICOM and equipment

- **HL7:** `appcli hl7-mllp-inspect synthetic-frame.bin --authorize-synthetic` examines locally supplied synthetic MLLP data. There is **no** production network MLLP sender/listener with ACK handling.
- **DICOM:** `appcli dicom-synthetic synthetic-image.dcm --authorize-synthetic` performs local metadata inspection using optional `pydicom`, stopping before pixels. No PACS/DICOMweb network integration.
- **Equipment:** `appcli device-snapshot synthetic-status.json --authorize-synthetic` reads a passive test snapshot; it sends **no** device commands.

## 5. CI integration

GitHub Actions runs unit tests and selected synthetic qualification demos. The v0.5 PR impact advisory maps changed source files to test IDs and conservatively escalates unmapped changes. **Advisory does not equal approval**. Review `.github/workflows/tests.yml`, `healthqualify/ci_impact.py` and [Issue hardening](ISSUE_HARDENING.md).

For your own CI, keep the seeded LIS demo's **expected exit 1** separate from actual unit test failures, store artifacts and independently record manifest digests, and require human disposition of failures.

## 6. Docker

`docker compose build` and `docker compose run --rm healthqualify` initialize a local developer SQLite volume. Compose deliberately **does not publish port 8877** or create a deployed service. Production deployment, secret storage, monitoring, backups, TLS and regulatory assessment are outside current scope.

---

### Continue exploring

[developer architecture](DEVELOPER_ARCHITECTURE.md) · [cli reference](CLI_REFERENCE.md) · [All guides](README.md) · [Project homepage](../README.md)
