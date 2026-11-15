# Synthetic qualification plan & protocol — TEMPLATE

**Draft, not approved.** Do not use as a released regulated protocol without organization-specific review.

## Identity
- Project/system ID:
- Intended use and exclusions:
- Baseline build SHA, version and environment:
- Owner/author and required independent reviewer:
- Source reference(s) with exact revision:
- Data classification: synthetic/public only

## Strategy
- Reason for testing and assessed risks:
- Why selected testing pathway (e.g., risk-based CSA or IQ/OQ/PQ) is appropriate:
- Test environment setup/configuration:
- Preconditions, fixtures, provenance and cleanup:
- Acceptance criteria and stopping rules:
- Evidence retention and independent manifest trust process:
- Handling FAIL / ERROR / NOT_RUN and deviations:

## Test procedure row

| Field | Example |
| --- | --- |
| Requirement | URS-001 |
| Test ID / phase | IQ-001 / IQ |
| Objective | Verify synthetic fixture's declared version |
| Preconditions | Local offline protocol, no network |
| Action | Execute strict protocol with v05cli |
| Expected | `runtime_version` equals `1.0` |
| Actual | Recorded by deterministic runner |
| Pass criteria | Only exact equality; otherwise FAIL |
| Evidence | Exact protocol, results, manifest + separately stored digest |
| Reviewer | External approved QA disposition pending |

## Deviations and requalification
Record issue ID, severity, affected requirements, correction, new-run evidence, review outcome and change-impact disposition. Never rewrite original result files.

## Sign-off (external QMS only)
Human approval control reference: ________; reviewer: ________; date: ________; status: **NOT APPROVED**.
