# Evaluate HealthQualify in 30–60 minutes

**Audience:** prospective maintainers, developers, IT integration testers, validation engineers and QA reviewers. **Outcome:** reproducibly demonstrate developer-alpha strengths/limitations with fictional inputs—**not** a purchase recommendation or production approval.

## Prerequisites (5–10 minutes)

Python 3.12 preferred, Git, non-production workstation, permission to download open-source dependencies. No PHI, hospital connections or API key needed. Clone and run unit tests:

```bash
git clone https://github.com/Tec-Wel/HealthQualify.git
cd HealthQualify
python -m unittest discover -s tests -v
```

**Pass criterion:** unit tests complete. Save OS/Python/Git SHA and evidence of the run; do not mistake tests for regulated qualification.

## Scenario A: seeded defect detection (10 minutes)

```bash
python -m healthqualify.v05cli run examples/synthetic_lis_v3/protocol.json --out .healthqualify/eval-lis
```

**Expected:** 2 PASS, 5 FAIL, **process exit 1**, `qualification_approved: false`. Inspect `results.json` and find mismatched HL7 patient ID, incorrect unit, missing critical notification, improper cross-tenant authorization and absent audit. Record whether findings are understandable and trace back to requirements.

## Scenario B: verify provenance (5–10 minutes)

Copy printed `manifest_sha256` **outside** the evidence directory and verify:

```bash
python -m healthqualify.v05cli verify .healthqualify/eval-lis --trusted-manifest-sha256 SAVED_DIGEST
```

**Expected:** `verified: true`. On a throwaway evidence copy, tamper with `results.json`; repeat using original digest. **Expected:** `verified: false`. Do not overwrite original evidence.

## Scenario C: assess code changes (5 minutes)

```bash
python -m healthqualify.v05cli impact examples/synthetic_lis_v3/protocol.json healthqualify/healthcare.py
python -m healthqualify.v05cli impact examples/synthetic_lis_v3/protocol.json src/unmapped.py
```

Expected: `REVIEW_REQUIRED` with mapped HL7 cases and `UNKNOWN_IMPACT` with all cases. **Neither approves a release.**

## Scenario D: create your own fixture (10–20 minutes)

Copy [synthetic protocol template](../examples/templates/strict-synthetic-protocol.json) into `my-eval-protocol.json`, run into a fresh directory, and confirm **one PASS** for the fixture version. Change `fixtures.runtime_version` to `"2.0"`; rerun into another directory and confirm **one FAIL**. This demonstrates deterministic behavior and reproducible new-run evidence, **not** a live application test.

## Evaluation scorecard

| Dimension | Evidence to gather | Green technical result | Not established |
| --- | --- | --- | --- |
| Ease of local setup | Versions, install issues, setup commands | Unit suite launches | Enterprise rollout |
| Defect detection | 5 seeded negatives | All five detected | Unknown real-world defect recall |
| Traceability | Requirement IDs and test outcomes | Direct links exist | Complete regulatory coverage |
| Integrity | Independent manifest digest, replay | Correct accept/reject behavior | Independent trusted timestamp / immutable archive |
| Change impact | Mapped/unmapped paths | Conservative recommendation | Full dependency proof |
| Extensibility | Custom source change plan | Can add safe tests with PR | Installable plugin ecosystem |
| Security | Loopback/access/synthetic policy | Boundaries upheld | HIPAA, tenant isolation, pentest |
| Regulatory readiness | Safety warnings/gates | No automatic approvals | Qualified QMS/e-signatures |

## Go/no-go decision

**Go for further engineering evaluation** if the demo is reproducible, scope boundaries fit your experiment and maintainers can address gaps. **No-go for regulated production** until independent product security, intended-use validation, operational controls, regulatory applicability, retention and QMS requirements have been met.

Use [Feature matrix](FEATURE_MATRIX.md), [Production readiness checklist](PRODUCTION_READINESS_CHECKLIST.md), and [FAQ](FAQ.md).
