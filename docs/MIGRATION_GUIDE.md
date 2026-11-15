# Migration planning from existing scripts and validation records

HealthQualify **does not currently provide a general-purpose import/migration command** for Excel/Word requirements, vendor QMS, Jira, pytest or GitHub project data. This guide is an **assessment and manual mapping approach**, not a claim of automated migration.

## Inventory before migrating

List sources: requirements files, risk records, protocol versions, scripts, outcomes, test environment, build/release IDs, QA signatures, deviations and evidence retention policies. Determine data classification before export; **do not put PHI or protected regulated records into the developer alpha**.

## Map legacy concepts carefully

| Existing item | Potential target | What remains manual |
| --- | --- | --- |
| Requirement sheet row | v0.3 `requirements[id,risk,acceptance_basis,source_id]` | Official source/version verification |
| Test case / pytest function | Allowlisted `tests` against embedded fixtures | Rewrite logic; no arbitrary Python invocation through JSON |
| Risk register | `risk` and external template | Detailed rationale, review and QMS record |
| CI changed files | `component_paths` mapping and `impact` | Dependency/unknown-impact review |
| Evidence archive | v0.5 new-run bundle and separately trusted digest | Authentic provenance and retention migration |
| QMS deviation | Separate workspace finding and offline handoff | Validated QMS synchronization and approval |
| Existing protocol v0.2 | SQLite `appcli protocol-add` | System UUID mapping and baseline review |
| Strict v0.3 protocol | Standalone `v05cli run` | No direct SQLite import |

## Pilot migration procedure

1. Select **one low-risk, completely synthetic** workflow.
2. Record the original source/fixture data and revision in a traceability worksheet.
3. Copy `examples/templates/strict-synthetic-protocol.json`, replace fictional requirements and safe fixtures.
4. Ensure each test maps to repository-relative code paths; flag unknown dependencies.
5. Execute and verify the new run; compare outcomes **manually** to your baseline test methodology.
6. Log mismatches and unsupported assertion types. Do not silently convert missing coverage to PASS.
7. Decide whether a reviewed custom adapter is appropriate. Only then scale to another protocol.
8. Preserve old records in the original controlled system until migration/retention authority approves an alternate disposition.

## Migration acceptance gate

For each requirement: source verified, risk assigned, acceptance criterion testable, technical test linked, evidence verifiable, gaps accounted for, reviewing authority identified, source tool validated for intended use. Never call a reconstructed synthetic report equivalent to an original executed clinical acceptance test.

For details see [User guide](USER_GUIDE.md), [Custom adapter guide](CUSTOM_ADAPTER_GUIDE.md), [Validation templates](VALIDATION_TEMPLATES.md).
