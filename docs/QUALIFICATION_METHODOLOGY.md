![Healthcare QA documentation](assets/category-health.svg)

[← **Documentation home**](README.md) &nbsp; / &nbsp; **Healthcare QA**

# Qualification methodology: risk-based and evidence-led

> **What you'll learn:** Apply risk-based requirements, protocols, execution evidence, deviations and human review.

**On this page:** [Eight-stage method](#eight-stage-method) · [Traceability example (entirely fictional)](#traceability-example-entirely-fictional) · [Core evidence pack](#core-evidence-pack) · [Present implementation mapping](#present-implementation-mapping)

---


This guide explains a disciplined technical workflow, **not** professional legal/regulatory advice or certification. Determine the applicable framework by intended use, jurisdiction, regulated role and quality system. IQ/OQ/PQ and CSA are alternative/complementary techniques **where justified**, not labels to apply blindly.

## Eight-stage method

### 1. Define system and intended use
State software owner, version/build SHA, operating environment, key interfaces, users, purpose, use boundaries and controlled scope. A fixture labelled “synthetic” must not be treated as a production sampling exercise.

### 2. Determine applicability
Document candidate regulations, guidance or standards, precise source/version and the basis for applicability or exclusion. Distinguish binding requirements from guidance and interoperability specifications. Human experts must review legal determinations.

### 3. Capture requirements (URS / FRS)
Use an ID, unambiguous expected behavior, testable acceptance basis, source and revision. Example `URS-002: synthetic PID-3 must equal P123` is testable; “system is fully compliant” is not.

### 4. Assess risk
Record severity/likelihood as appropriate to your organizational policy, whether a failure affects safety/data integrity/availability/security, and why a test depth is appropriate. HealthQualify's `low/medium/high/critical` tags **do not** substitute for a validated risk matrix.

### 5. Create protocol
Every requirement must link to executable tests or have documented justified manual verification. **IQ** may confirm installation/environment characteristics; **OQ** challenge behavior and negative conditions; **PQ** exercise representative intended workflows. In a CSA setting, choose assurance evidence proportional to risk.

### 6. Execute deterministically
Do not let optional AI decide PASS/FAIL. Preserve `PASS`, `FAIL`, `ERROR`, `NOT_RUN` independently. Verify fixture origins, environment, build, protocol digest and execution conditions.

### 7. Investigate and review
A FAIL triggers discrepancy analysis, evidence preservation, root-cause investigation, corrective action and retesting appropriate to impact. A reviewer may record `RETEST_REQUIRED`, `REJECTED` or `ACCEPT_WITH_JUSTIFICATION` in the current technical workflow; **this does not close or approve a regulated deviation**.

### 8. Requalification after change
Use versioned baselines, changed-file mapping and conservative `UNKNOWN_IMPACT` escalation. Reassess risk and affected requirements, produce new evidence, obtain an independently controlled disposition. **No code path currently auto-approves a release.**

## Traceability example (entirely fictional)

| Source | Requirement | Risk | Test | Fixture observation | Result | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| SYNTH-LIS-2026 | URS-002: correct PID-3 | high | OQ-001 | P999 vs P123 | FAIL | Investigate mapping |
| SYNTH-LIS-2026 | URS-007: FHIR resource type | medium | OQ-005 | Observation | PASS | Record coverage only |
| SYNTH-LIS-2026 | URS-006: audit record | high | PQ-001 | missing | FAIL | Investigate and retest |

## Core evidence pack

- System/intended-use record and source version
- Requirements and risk rationale
- Protocol with explicit acceptance criteria and version
- Test environment and exact build identifier
- Per-test raw technical outcomes and requirement coverage
- Deviations, evidence-linked retests, reviewer events
- Technical manifest, independently trusted digest and immutable/controlled store **outside alpha if needed**
- Change-impact review and final separately controlled QMS disposition

## Present implementation mapping

**Standalone v0.5:** strict offline v0.3 protocol, deterministic fixture execution, manifest verification and source impact. **SQLite workspace:** v0.2 baseline and run records, deviations/audit. **v0.6:** QA deviation review, QMS handoff, retention metadata, release advisory. These tracks are not automatically one continuous regulated workflow.

See [End-to-end workflow](END_TO_END_WORKFLOW.md), [Templates](VALIDATION_TEMPLATES.md), and [Regulatory mapping](REGULATORY_MAPPING.md).

---

### Continue exploring

[healthcare use cases](HEALTHCARE_USE_CASES.md) · [validation templates](VALIDATION_TEMPLATES.md) · [All guides](README.md) · [Project homepage](../README.md)
