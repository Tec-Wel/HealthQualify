![Healthcare QA documentation](assets/category-health.svg)

[← **Documentation home**](README.md) &nbsp; / &nbsp; **Healthcare QA**

# Healthcare use cases: what can be tested today?

> **What you'll learn:** Explore realistic healthcare test scenarios and understand which integration checks are available today.

**On this page:** [Use case 1 — LIS ↔ EHR data quality](#use-case-1-lis-ehr-data-quality) · [Use case 2 — FHIR API read-only staging smoke check](#use-case-2-fhir-api-read-only-staging-smoke-check) · [Use case 3 — Hospital software access control](#use-case-3-hospital-software-access-control) · [Use case 4 — DICOM metadata](#use-case-4-dicom-metadata)

---


**Scope:** synthetic developer-alpha demonstrations. Intended use, standards applicability and test protocols must be assessed independently for each institution. No PHI, live patient system or production equipment access.

## Use case 1 — LIS ↔ EHR data quality

**Scenario:** a laboratory result transmitted as synthetic HL7 v2 must preserve correct patient/sample identity, result units, critical-result acknowledgment and audit event.

**Current tooling:** `examples/synthetic_lis_v3/protocol.json`, deterministic HL7-field assertion, equality/presence/authorization checks, traceability and evidence verification.

```bash
python -m healthqualify.v05cli run examples/synthetic_lis_v3/protocol.json --out .healthqualify/lis-example
```

The example **intentionally finds five defects** (identity, units, acknowledgment, cross-tenant access and audit). It is not an MLLP server, live integration harness or clinical result verification.

**Reviewer questions:** Is each acceptance criterion source-backed? Does the fixture represent a verified interface contract? Are high-risk negative cases included? Was each change assessed? Are reports trusted and preserved?

## Use case 2 — FHIR API read-only staging smoke check

**Scenario:** verify an authorized non-production FHIR endpoint returns `resourceType: Observation`. **Current tooling:** `appcli fhir-check-approved` with exact approved HTTPS origin and read-only bearer token supplied at runtime. This is a **single-field assertion**, not full FHIR profile validation or SMART interoperability.

**Evidence:** preserve sanitized outcome and authorized endpoint environment identity externally; avoid raw observations containing personal identifiers.

## Use case 3 — Hospital software access control

**Scenario:** synthetic multi-tenant authorization must reject access outside the requesting user's permitted tenant. **Current tooling:** embedded `role_denied` fixture check and standalone requirements mapping. It does not generate accounts, exercise real IAM or verify production tenant isolation.

**Negative criteria:** a fixture containing `allowed: true` must fail the cross-tenant-denial acceptance criterion.

## Use case 4 — DICOM metadata

**Scenario:** inspect a *synthetic* DICOM file offline. **Current tooling:** `appcli dicom-synthetic FILE --authorize-synthetic` with optional pydicom dependency. It reads metadata without pixels; no PACS communication or diagnostic image assurance.

## Use case 5 — Medical equipment status snapshot

**Scenario:** validate a passive, already captured synthetic telemetry object. **Current tooling:** `appcli device-snapshot FILE --authorize-synthetic`. This does **not** connect to, command, calibrate, or control equipment.

## Use case 6 — Release requalification

**Scenario:** a software update changes the LIS parser. Source-path mapping identifies the two relevant HL7 tests. Unmapped changes result in `UNKNOWN_IMPACT` and a full-test recommendation.

```bash
python -m healthqualify.v05cli impact examples/synthetic_lis_v3/protocol.json healthqualify/healthcare.py
```

Release event automation generates an advisory review package, not an approval or deployment control.

## Use case 7 — QA investigation and offline QMS handoff

A separate SQLite v0.2 workspace stores a run with deviations. A QA reviewer can authenticate and record a constrained disposition, export an offline QMS package, and retain a technical checksum record with a legal-hold flag. **Important:** handoff is not a validated QMS connector; retention is not WORM enforcement.

See [v0.6 quality review](QUALITY_RELEASE_BENCHMARK_V06.md) and [Qualification methodology](QUALIFICATION_METHODOLOGY.md).

## Suggested acceptance matrix

For any project, define **system boundary**, **data classification**, **requirement source**, **risk**, **acceptance assertion**, **fixture origin**, **test ID**, **expected result**, **evidence trust anchor**, **reviewer** and **open gap**. Use [Validation templates](VALIDATION_TEMPLATES.md) to capture these before extending the code.

---

### Continue exploring

[qualification methodology](QUALIFICATION_METHODOLOGY.md) · [validation templates](VALIDATION_TEMPLATES.md) · [All guides](README.md) · [Project homepage](../README.md)
