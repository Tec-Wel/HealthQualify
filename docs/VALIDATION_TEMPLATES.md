# Reusable synthetic qualification templates

**Status:** example *engineering worksheets*. None are approved URS/FRS, IQ/OQ/PQ documents, Part 11 records, regulatory compliance checklists, or evidence of completed validation. Use them to draft materials for **independent human QA review**.

## Package contents

- [System and risk template](../examples/templates/system-risk-template.md)
- [Requirements–test traceability matrix](../examples/templates/traceability-template.csv)
- [Qualification plan / protocol](../examples/templates/qualification-plan-template.md)
- [Deviation / investigation / retest](../examples/templates/deviation-template.md)
- [Release impact and disposition checklist](../examples/templates/release-review-template.md)
- [Executable strict v0.3 synthetic JSON example](../examples/templates/strict-synthetic-protocol.json)

Templates show **what to capture** and include fictional sample values. They do not automatically create validated QMS records or an electronic-signature process.

## How to use the pack

1. Describe system intended use, configuration, owner, environment and build/version.
2. Identify the authoritative user or software requirement sources. Never invent approval status.
3. Create stable requirement IDs, measurable acceptance basis, risk justification and verification plan.
4. Map each requirement to a test ID and test phase when appropriate; list manual/uncovered checks explicitly.
5. Copy the strict synthetic protocol to your own file and modify only safe, non-sensitive fixtures.
6. Execute with `python -m healthqualify.v05cli run MY_FILE --out NEW_DIR`.
7. Save manifest SHA-256 **outside** the report bundle and verify it with `v05cli verify`.
8. For FAIL/ERROR/NOT_RUN, investigate and create a new run; never edit old evidence.
9. Obtain any required review/approval outside the alpha, under the organization's independently controlled QMS.

## Traceability example

| Source | Requirement | Risk | Criterion | Test | Expected | Observed | Review |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SYNTH-BOOK-1 | URS-001 | low | Fixture version equals 1.0 | IQ-001 | 1.0 | 1.0 | PASS, technical only |
| SYNTH-LIS-2026 | URS-002 | high | PID-3 equals synthetic P123 | OQ-001 | P123 | P999 | FAIL; investigate |
| SYNTH-LIS-2026 | URS-006 | high | Audit event exists | PQ-001 | present | missing | FAIL; investigate |

Do not combine outcomes from different fixture systems into a single project evidence run; this table is illustrative.

## Template quality rules

Every template should be clear about **who owns the record**, **which revision it describes**, **which risk it addresses**, **what constitutes acceptance**, **where the evidence lives**, **how to verify it independently**, and **what cannot be decided by the software**.

See [Qualification methodology](QUALIFICATION_METHODOLOGY.md) and [Verification](VERIFICATION_GUIDE.md).
