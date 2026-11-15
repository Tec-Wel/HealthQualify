# Feature and maturity matrix

**Version basis:** inspect the checked-out commit and [Release status](RELEASE_STATUS.md) because these capabilities are actively evolving. Status here is developer-alpha behavior; no item is “production validated.”

| Feature | Status | Where | What users must not assume |
| --- | --- | --- | --- |
| v0.1/0.2 deterministic synthetic checks | Implemented alpha | `healthqualify.cli`, `assurance.py` | Live software end-to-end testing |
| Strict v0.3 offline synthetic protocol | Implemented alpha | `protocol_v3.py`, `v05cli` | Arbitrary test-code execution |
| Requirement-to-test traceability | Implemented alpha for fixtures | `assurance.py`, `results.json` | Complete regulatory coverage |
| SHA-256 manifest + replay | Implemented alpha | `evidence_v3.py` | Trusted timestamps/WORM/e-signatures |
| Code-path impact advisory | Implemented alpha | `change_graph.py`, `ci_impact.py` | Complete dependency discovery |
| SQLite system registry/draft/baseline/run | Implemented alpha | `workspace.py`, `appcli.py` | Native v0.3 import / formal approval |
| Controlled QA deviation review | Implemented alpha | `deviation_review.py`, `quality_cli.py` | Deviation closure or valid QMS signature |
| Offline QMS handoff JSON | Implemented alpha | `quality_cli qms-export` | Validated live vendor integration |
| Release tag impact plan | Implemented alpha | `release_ci.py`, workflow | Deployment blocking/release approval |
| Technical evidence retention metadata | Implemented alpha | `retention.py` | OS-enforced WORM/regulated retention |
| Secure loopback API | Implemented alpha | `secure_api.py` | TLS public API, SSO/MFA, tenants |
| Local synthetic REST GET assertion | Implemented alpha | `rest_local.py` | Arbitrary URLs or writes |
| Approved read-only FHIR field check | Restricted prototype | `fhir_secure.py` | FHIR conformance or PHI handling |
| HL7 MLLP frame inspection | Offline prototype | `hl7_mllp.py` | Network listener/sender/ACK |
| DICOM metadata inspection | Offline prototype | `dicom_device.py` | PACS/DICOMweb/image diagnosis |
| Passive equipment snapshot | Offline prototype | `dicom_device.py` | Remote equipment control/calibration |
| Local Ollama drafts | Optional experimental | `ai.py` | Authoritative AI verdicts/approvals |
| Internal three-run benchmark | Synthetic benchmark | `benchmarks/` | Verified speed or quality superiority |
| Docker Compose | Local initialization only | `compose.yaml` | Cloud production stack |
| Cloud multi-tenant / PostgreSQL | Planned | Roadmap | Deployed or validated |
| Qualified electronic signatures | Not supported | N/A | Part 11 compliance |
| Regulated production/PHI | Not supported | N/A | Authorization for clinical use |
| Pluggable adapters marketplace | Not supported | N/A | External installable plugin mechanism |

## Definition of “implemented”

A feature has code and representative tests, subject to safety and capability limits. **Implemented alpha ≠ independently validated ≠ regulatory-ready ≠ enterprise-secure**.

Before deciding whether to adopt a feature, inspect [Evaluation guide](EVALUATION_GUIDE.md), [Security model](SECURITY_MODEL.md), and [Production readiness checklist](PRODUCTION_READINESS_CHECKLIST.md).
