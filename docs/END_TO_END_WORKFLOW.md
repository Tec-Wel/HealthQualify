# End-to-end workflow: from project definition to evidence review

This is a **hands-on two-track tutorial**. It separates (A) a working v0.5 offline evidence demonstration from (B) a v0.3 SQLite workspace that stores v0.2 protocol draft/baseline/review records. They are complementary **but not automatically integrated**.

## Workflow at a glance

```text
Intended use → requirements and risk → measurable synthetic fixtures
            → deterministic execution → findings and traceability
            → artifact integrity verification → human investigation
            → new test/retest → impact assessment → human disposition
```

This is an *engineering reference workflow*. Formal approvals, electronic signatures, live production integrations and legal qualification are not included.

## Track A: execute and verify a v0.5 strict synthetic protocol

**Step A1.** Clone and test the repository (see [Installation](INSTALLATION.md)). **Step A2.** Read `examples/synthetic_lis_v3/protocol.json` and match its seven requirement IDs to seven tests and their fixture values. **Step A3.** Execute:

```bash
python -m healthqualify.v05cli run examples/synthetic_lis_v3/protocol.json --out .healthqualify/lis-a1
```

**Expected:** exit code 1 because of five seeded defects; the output JSON reports **2 PASS, 5 FAIL**. This is an intentionally negative scenario.

**Step A4.** Record the printed `manifest_sha256` in a trusted independent location, inspect the result file, and verify:

```bash
python -m json.tool .healthqualify/lis-a1/results.json
python -m healthqualify.v05cli verify .healthqualify/lis-a1 --trusted-manifest-sha256 YOUR_SAVED_DIGEST
```

**Step A5.** Investigate the failed requirements. Do **not** modify the recorded `results.json`; it is evidence of the old execution. Instead copy the original protocol to another working file, change **synthetic fixtures** to simulate your correction, and rerun into **another output directory**. Keep both old and new reports for review. A passing rerun confirms the amended fixture, not a repaired hospital deployment.

**Step A6.** On a subsequent software revision, ask which mapped cases need attention:

```bash
python -m healthqualify.v05cli impact examples/synthetic_lis_v3/protocol.json healthqualify/healthcare.py
```

The output is advisory and always requires human review.

## Track B: local SQLite system, protocol review, run and report

This track uses the shipped **v0.2** example `examples/synthetic_lis_v2/protocol.json`, not the v0.3 file above.

**Step B1. Initialize a local-only database and register a system:**

```bash
python -m healthqualify.appcli --db healthqualify.db init
python -m healthqualify.appcli --db healthqualify.db system-add "LIS Demo" "Synthetic laboratory interface validation exercise" "Engineer"
```

Copy the `id` returned by `system-add` (a UUID).

**Step B2. Make a separate protocol file:** copy `examples/synthetic_lis_v2/protocol.json` to `my-lis-v2.json` and replace **only** `system.id` with that UUID. Keep the example itself unchanged.

**Step B3. Draft in the workspace:**

```bash
python -m healthqualify.appcli --db healthqualify.db protocol-add YOUR_SYSTEM_UUID my-lis-v2.json Engineer
python -m healthqualify.appcli --db healthqualify.db protocols
```

Capture the returned protocol UUID.

**Step B4. Record a separate-person demo baseline event:**

```bash
python -m healthqualify.appcli --db healthqualify.db baseline YOUR_PROTOCOL_UUID Reviewer "Reviewed synthetic acceptance criteria"
```

The reviewer string must differ from the author. This is a local developer record and **not a Part 11 signature**.

**Step B5. Execute, inspect findings and export:**

```bash
python -m healthqualify.appcli --db healthqualify.db run YOUR_PROTOCOL_UUID Engineer
python -m healthqualify.appcli --db healthqualify.db deviations
python -m healthqualify.appcli --db healthqualify.db runs
python -m healthqualify.appcli --db healthqualify.db audit
python -m healthqualify.appcli --db healthqualify.db report YOUR_RUN_UUID .healthqualify/workspace-report
```

Capture the `run_id` from the `run` output. The workspace records findings and per-test evidence references for synthetic cases. Local reports are **technical**, not protected regulated records. See [Verification](VERIFICATION_GUIDE.md).

**Step B6. Investigate each finding:** document suspected cause, risk and planned correction in your organization-controlled record. The workspace's `disposition` method requires a distinct passing same-protocol retest; no general-purpose deviation-close CLI command is exposed. Do not say it is automatically closed.

## Human review checklist

- Is the documented intended use accurate and is the environment authorized?
- Are all important requirements linked to defensible acceptance criteria and at least one executed check?
- Are failures, errors, or unexecuted cases retained and investigated?
- Is there an independently trusted digest outside the artifacts?
- Was changed code assessed, including `UNKNOWN_IMPACT`?
- Were reviewers independent where your process requires it?
- Are evidence retention, data privacy, QMS and regulatory requirements satisfied **outside** this alpha?

## Outcome and next steps

A successful technical demo yields an intelligible chain from synthetic inputs to reproducible results. It does **not** certify that a clinical system has been validated. For syntax, see [Configuration](CONFIGURATION.md); for underlying constraints, [Security & limitations](SECURITY_AND_LIMITATIONS.md).
