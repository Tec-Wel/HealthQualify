![Start here documentation](assets/category-start.svg)

[← **Documentation home**](README.md) &nbsp; / &nbsp; **Start here**

# User guide: apply HealthQualify to your own project

> **What you'll learn:** Apply HealthQualify's two supported protocol tracks and deterministic assertions to a synthetic project.

**On this page:** [Choose the right path](#choose-the-right-path) · [Start with the project contract](#start-with-the-project-contract) · [Create a fixture-backed protocol](#create-a-fixture-backed-protocol) · [Execute and inspect](#execute-and-inspect)

---


HealthQualify should help you answer **what was intended, what was actually checked, which requirement each check supports, what failed, and which evidence is trustworthy**. This guide is for **developer-alpha, non-production, synthetic-data qualification experiments**.

## Choose the right path

| Your task | Use | Protocol |
| --- | --- | --- |
| Run verifiable offline fixture assertions and code impact | `python -m healthqualify.v05cli` | Strict `schema_version: "0.3"` |
| Keep local project, review and run records | `python -m healthqualify.appcli` | v0.2 workspace protocol |
| Run older standalone demonstrations | `python -m healthqualify.cli` | v0.1/v0.2 |
| Read from an approved test-only FHIR or local REST server | Explicitly authorized adapter | One-off read-only assertion |

**Important:** there is currently **no automatic bridge** that imports a v0.5 v0.3 protocol into the SQLite workspace. The workspace accepts v0.2 protocols; keep their schema formats separate.

## Start with the project contract

Before writing a protocol, record the system name, owner, intended use, version/build identifier, test environment, source of truth for requirements, acceptance criteria, risks and authorized sample data. Do not assert regulatory applicability automatically.

Example: “Synthetic appointment booking service, revision 1.0, test-only, should reject unavailable times and avoid cross-tenant access.” Choose *measurable assertions*. A statement like “system is safe and compliant” is not an executable acceptance test.

## Create a fixture-backed protocol

1. Copy `examples/synthetic_lis_v3/protocol.json` to a **new local file outside the tracked example directory**.
2. Give your system a clear `id`, `version`, `intended_use`, `environment`, and **full 40-character** `build_sha` (use the real Git commit of your test fixture if available, rather than a fabricated production identity).
3. For each requirement, add a unique ID, explicit risk, `acceptance_basis`, and `source_id`.
4. Register every `source_id` in `source_references` with a descriptive reference; the current runner checks linkage, **not source authenticity**.
5. Add synthetic fixture values under `fixtures`.
6. Add each test's unique `id`, qualification `phase`, `requirement_ids`, allowlisted `check`, `fixture`, expected values as applicable and `component_paths` with repository-relative source paths.
7. Keep `qualification_state: "draft"`, `approval_reference: null`, and `execution_policy.network`, `destructive`, `allow_ai` as `false`.
8. Ensure `data_classification` is `synthetic` or `public`. Never insert PHI.

See [Configuration](CONFIGURATION.md) for a minimal specimen and field-by-field explanations. Refer to the shipped protocol as the executable schema example.

## Execute and inspect

```bash
python -m healthqualify.v05cli run my-protocol.json --out .healthqualify/my-project-001
python -m json.tool .healthqualify/my-project-001/results.json
```

Store the printed manifest digest separately, then invoke `verify` with `--trusted-manifest-sha256` (see [Verification](VERIFICATION_GUIDE.md)). Test outcomes reflect the supplied synthetic observations. **Changing a fixture changes the simulated world, not your deployed application.**

## What “use it on my own project” currently means

**Supported now:** you can model your system's requirements, synthetic inputs, allowed deterministic checks, component-to-test mapping and review of technical evidence. You can separately use restricted one-off test-only REST/FHIR assertions. You can use v0.2 workspace lifecycle records for a synthetic project.

**Not supported as a turnkey product:** pointing HealthQualify at any GitHub URL and automatically discovering requirements, connecting to production EHR/PACS/equipment, executing arbitrary end-to-end business flows, signing legal approvals or certifying FDA/GxP compliance. Those tasks need specialized adapters, documented authorization, QMS controls and additional engineering.

## How to interpret outcomes

- `PASS`: observed synthetic fixture satisfied this specific assertion.
- `FAIL`: observed fixture violated a defined assertion. Investigate the discrepancy.
- `ERROR`: check failed to execute reliably. Do not treat it as a pass.
- `NOT_RUN`: execution or coverage is absent; coverage is incomplete.
- `qualification_approved: false`: technical results cannot independently approve qualification.

A test passing does not establish that other requirements are covered. A high-risk requirement needs a justified verification strategy, not merely more green checks.

## Handling change

If a source path changes, run:

```bash
python -m healthqualify.v05cli impact my-protocol.json src/booking/service.py
```

Mapped changes return targeted recommendations and require human review. Unknown paths return all tests and `UNKNOWN_IMPACT`. The file map does **not** infer import graphs or guarantee full dependency discovery.

## When the project needs formal validation

Work with your organization's QA/regulatory owners to assess intended use, risk, jurisdiction, appropriate assurance approach, test-environment controls, independent review, traceability, retention, electronic record obligations, and the validation of HealthQualify itself. The current repository does not meet those operational gates.

Next: [End-to-end workflow](END_TO_END_WORKFLOW.md) · [Examples](EXAMPLES.md) · [Security & limitations](SECURITY_AND_LIMITATIONS.md).

---

### Continue exploring

[getting started](GETTING_STARTED.md) · [end to end workflow](END_TO_END_WORKFLOW.md) · [All guides](README.md) · [Project homepage](../README.md)
