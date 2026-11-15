![Start here documentation](assets/category-start.svg)

[← **Documentation home**](README.md) &nbsp; / &nbsp; **Start here**

# Examples: learn from reproducible synthetic projects

> **What you'll learn:** Try representative LIS, local REST, read-only FHIR, and change-impact examples using fictional data.

**On this page:** [A. Laboratory Information System (LIS) — complete fixture](#a-laboratory-information-system-lis-complete-fixture) · [B. Restricted local JSON REST assertion](#b-restricted-local-json-rest-assertion) · [C. FHIR Observation staged read](#c-fhir-observation-staged-read) · [D. Simulate impact of a code change](#d-simulate-impact-of-a-code-change)

---


All examples are **educational**, use synthetic/public values, and should not be promoted to production qualification claims.

## A. Laboratory Information System (LIS) — complete fixture

**Source:** `examples/synthetic_lis_v3/protocol.json` (strict v0.3 schema). Run:

```bash
python -m healthqualify.v05cli run examples/synthetic_lis_v3/protocol.json --out .healthqualify/example-lis
```

| Requirement | Check | Built-in result | Why |
| --- | --- | --- | --- |
| URS-001 | IQ runtime equals 1.4.2 | PASS | Embedded version matches |
| URS-002 | OQ HL7 PID-3 matches synthetic ID | FAIL | Mismatch in fixture |
| URS-003 | OQ HL7 OBX-6 correct units | FAIL | Units differ |
| URS-004 | OQ critical notification present | FAIL | Flag false |
| URS-005 | OQ cross-tenant access denied | FAIL | Fixture allows access |
| URS-006 | PQ audit record present | FAIL | No audit event |
| URS-007 | OQ FHIR `resourceType` | PASS | Synthetic resource is Observation |

**Acceptance:** execution reports 2 PASS and 5 FAIL with exit 1. Save the printed digest and verify it as explained in [Verification](VERIFICATION_GUIDE.md).

**How to customize safely:** copy the JSON into a new file; update system/build metadata, each source reference and acceptance basis, fixture values, test mappings and expected assertions. Ensure the check types are among those supported by the shipped runner. Do not assume the runner can open a remote LIS or process patient records.

## B. Restricted local JSON REST assertion

For a **locally running, synthetic and explicitly authorized** JSON service:

```bash
python -m healthqualify.v05cli rest-check-local http://127.0.0.1:8000/test/example status '"ready"' --authorize-synthetic
```

This is an illustrative invocation; it will fail unless **you already started** a matching local server at a `/test/` URL returning JSON such as `{"status":"ready"}`. This command is a bounded **one-off assertion**, not a full protocol-run integration or arbitrary network scanner. See [Integration](INTEGRATION_GUIDE.md).

## C. FHIR Observation staged read

With a properly authorized non-production HTTPS service and external read-only credentials:

```bash
export HEALTHQUALIFY_FHIR_ORIGIN='https://fhir-staging.example.org'
export HEALTHQUALIFY_FHIR_BEARER='REPLACE_WITH_APPROVED_READ_ONLY_TOKEN'
python -m healthqualify.appcli fhir-check-approved https://fhir-staging.example.org/fhir/Observation/123 resourceType '"Observation"' --authorize-read-only
```

**No actual service is provided at the placeholder domain.** Do not commit bearer tokens; do not use production resources or PHI. This checks one field, not full FHIR conformance.

## D. Simulate impact of a code change

```bash
python -m healthqualify.v05cli impact examples/synthetic_lis_v3/protocol.json healthqualify/healthcare.py
python -m healthqualify.v05cli impact examples/synthetic_lis_v3/protocol.json src/unmapped.py
```

The first finds mapped test IDs and signals `REVIEW_REQUIRED`. The second signals `UNKNOWN_IMPACT` and recommends all seven tests. Neither is a release gate or approval.

## E. Synthetic workspace with findings and report

See [End-to-end workflow](END_TO_END_WORKFLOW.md) **Track B**. It uses v0.2 JSON stored in SQLite and a separate author/reviewer event. The workspace does not accept the strict v0.3 JSON file directly.

## F. Optional capabilities you should not misinterpret

The repository includes **offline** HL7 MLLP frame inspection, synthetic DICOM metadata inspection (optional pydicom dependency), passive equipment snapshots and internal ModelQual benchmarking. These are limited prototype checks, **not** bedside device control, DICOMweb, live HL7 listener/ACK validation or competitor performance claims. Consult [Security & interoperability](SECURITY_INTEROP_V04.md).

---

### Continue exploring

[getting started](GETTING_STARTED.md) · [end to end workflow](END_TO_END_WORKFLOW.md) · [All guides](README.md) · [Project homepage](../README.md)
