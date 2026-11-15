![Project reference documentation](assets/category-reference.svg)

[← **Documentation home**](README.md) &nbsp; / &nbsp; **Project reference**

# HealthQualify v0.3 local platform foundation

> **What you'll learn:** Explore the development history of the local workspace, database, API and integration prototypes.

**On this page:** [Status and scope](#status-and-scope) · [Installation](#installation) · [Local dashboard and API](#local-dashboard-and-api) · [Draft-only regulatory and AI](#draft-only-regulatory-and-ai)

---


## Status and scope
This is a working **local developer alpha**, not a production healthcare validation product. It is a first integrated product slice covering system registry, risk/URS helpers, draft protocol versioning, baseline review, synthetic execution, findings, audit events, reporting, regulatory references, optional local AI drafts, model evaluation, and a basic dashboard. It has **no regulatory electronic signatures, regulated-grade record protection, licensed quality system, PHI processing, or clinical data connectivity**.

## Installation
Python 3.10+ (stdlib only). From project root:
```bash
python -m unittest discover -s tests -v
python -m healthqualify.appcli --db /tmp/hq-demo.db init
python -m healthqualify.appcli frameworks
python -m healthqualify.appcli --db /tmp/hq-demo.db system-add "LIS Synthetic" "Demonstration" "Engineer"
```
The system command emits a UUID. For drafting, copy the bundled `examples/synthetic_lis_v2/protocol.json` to a separate local file and replace `system.id` with this UUID (do not edit the tracked reference fixture). Then:
```bash
python -m healthqualify.appcli --db /tmp/hq-demo.db protocol-add <system-uuid> <protocol-file> Engineer
python -m healthqualify.appcli --db /tmp/hq-demo.db protocols
python -m healthqualify.appcli --db /tmp/hq-demo.db baseline <protocol-uuid> Reviewer "Synthetic baseline review"
python -m healthqualify.appcli --db /tmp/hq-demo.db run <protocol-uuid> Engineer
python -m healthqualify.appcli --db /tmp/hq-demo.db deviations
python -m healthqualify.appcli --db /tmp/hq-demo.db report <run-uuid> /tmp/hq-report
```
The local baseline is a *demo reviewer event only*, **not a Part 11 compliant electronic signature**. No approval of the software's clinical or regulatory qualification is created.

## Local dashboard and API
Use a long random token:
```bash
export HEALTHQUALIFY_API_TOKEN="$(python -c 'import secrets;print(secrets.token_urlsafe(32))')"
python -m healthqualify.appcli --db /tmp/hq-demo.db serve
```
Open http://127.0.0.1:8765 locally. Read-only GET endpoints include `/api/frameworks`, `/api/systems`, `/api/protocols`, `/api/runs`, `/api/deviations`. Mutations require `Authorization: Bearer <token>` and JSON request bodies, for three endpoints: POST `/api/systems`, `/api/protocols`, `/api/runs`.

This API is a *single-user development prototype*, not a production authenticated, authorized, audited, privacy-compliant multi-tenant server. Never bind the API publicly or place a reverse proxy in front of it without implementing full security controls.

## Draft-only regulatory and AI
```bash
python -m healthqualify.appcli frameworks
python -m healthqualify.appcli draft-urs example-system.json example-needs.json
python -m healthqualify.appcli risk-plan example-system.json example-frameworks.json high
python -m healthqualify.appcli regulation-diff old.txt new.txt
python -m healthqualify.appcli agents
```
Regulatory applicability is explicitly supplied by a human; a regulatory reference is not a legal assessment. eCFR retrieval helper can access the official eCFR API only when invoked explicitly by code; the CLI defaults to no network activity.

Optional local model draft:
```bash
python -m healthqualify.appcli draft-agent oq llama3.2 sanitized-prompt.txt --allow-local-ai
```
This requires Ollama locally at 127.0.0.1:11434 and an installed model. No AI is installed or called by default. Never send PHI or sensitive regulated data.

## Cloud deployment
The Docker image is portable, but the provided Compose profile is explicitly **local-only**. AWS EC2, GCP and Azure VM, and hospital on-prem deployment require a secured ingress, RBAC, TLS, encrypted storage, backups, monitoring, threat model and appropriate validation work. The same container can be used in those environments; no production configuration is claimed to be implemented.

## Local interoperability and integrity prototypes

Explicitly authorized, read-only synthetic FHIR endpoint check on loopback:

```bash
python -m healthqualify.appcli fhir-check-local \
  http://127.0.0.1:8000/fhir/Observation/1 resourceType '"Observation"' --allow-local-http
```

A synthetic FHIR fixture server must be started separately; the unit tests mock it without network use. Public/clinical URLs are rejected.

Regulatory snapshots from operator-supplied text, not automatically verified official versions:

```bash
python -m healthqualify.appcli --db /tmp/hq-demo.db regwatch-capture us-part-11 supplied-text.txt
```

Optional shared-secret integrity receipt after exporting a report:

```bash
export HEALTHQUALIFY_EVIDENCE_KEY="$(python -c 'import secrets;print(secrets.token_urlsafe(48))')"
python -m healthqualify.appcli seal /tmp/hq-report
python -m healthqualify.appcli verify-seal /tmp/hq-report
```

Neither the local baseline event nor the receipt is a qualified electronic signature. See [release scope and gaps](RELEASE_STATUS.md).

## Gaps to full product
Real FHIR/HL7 authenticated adapters against approved environments; React UI; FastAPI service; PostgreSQL and object storage; role-based access and true approval workflow; durable signed evidence with trusted timestamps; privacy and security testing; real regulatory version tracking; physician/QA reviewed qualification packs; automated source-code change impact; and self-assurance of HealthQualify itself.

## Roadmap truth in labeling
Implemented means **demonstration functional**. It does not mean regulatory-ready or production-ready. IQ/OQ/PQ tests and CSA records should be selected according to intended use and an authorized quality review.

---

### Continue exploring

[release status](RELEASE_STATUS.md) · [roadmap](ROADMAP.md) · [All guides](README.md) · [Project homepage](../README.md)
