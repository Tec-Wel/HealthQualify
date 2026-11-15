# Synthetic system and risk register — TEMPLATE

> NOT APPROVED; educational example only. Replace all fictional values before using in a controlled process. No PHI.

| Field | Synthetic example / operator entry |
| --- | --- |
| System ID | SYNTH-BOOK-001 |
| Name | Fictional Appointment Scheduler |
| Intended use | Evaluate deterministic synthetic acceptance criteria only |
| Version/build | 1.0 / full Git SHA: __________________________ |
| Site / environment | Local test-only |
| Data classification | SYNTHETIC |
| Owner / author | Engineer |
| QMS control / approver | External to HealthQualify; not approved |
| Approved requirement sources | SYNTH-BOOK-1 (fictional spec) |
| Included interfaces | None; embedded fixtures |
| Excluded interfaces | Production EHR, SMS, payment, PHI, network writes |

## Risk records

| Risk ID | Linked URS | Failure mode | Severity/likelihood rationale | Controls | Test | Reviewer action |
| --- | --- | --- | --- | --- | --- | --- |
| R-001 | URS-001 | Wrong deployed version | Fictional low-risk version fixture | Version equality | IQ-001 | Confirm tested commit |
| R-002 | TBD | Cross-tenant booking disclosure | To assess; no real data allowed | Access denial, logging | OQ-TBD | Design negative test |

## Applicability decision

Regulated intended use? **UNDETERMINED**. Applicable framework and source revision: ________. Legal/QA reviewer and decision record: ________. Do not interpret technical PASS as regulatory approval.

## Revision and review log

| Revision | Change | Author | Review decision | Evidence reference |
| --- | --- | --- | --- | --- |
| Draft-1 | Initial synthetic example | Engineer | PENDING | None |
