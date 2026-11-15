# Verification and evidence integrity guide

## Three questions that must not be confused

1. **Did assertions execute?** Read `results.json` and the requirement traceability statuses. Some assertions may FAIL or be NOT_RUN.
2. **Are exported artifacts consistent with a trusted run?** Verify each artifact hash, the manifest against an **independently stored** digest, and deterministic replay.
3. **Is a system qualified for a regulatory purpose?** This needs a controlled QMS process, validated tools and site-specific human decisions. HealthQualify does **not** make that determination.

## v0.5 synthetic evidence recipe

```bash
python -m healthqualify.v05cli run examples/synthetic_lis_v3/protocol.json --out .healthqualify/check-001
```

The command prints a `manifest_sha256`. Treat that 64-character value as your **trust anchor**; copy it to a separate access-controlled record. Then:

```bash
python -m healthqualify.v05cli verify .healthqualify/check-001 --trusted-manifest-sha256 YOUR_SAVED_DIGEST
```

`verified: true` means the verifier confirmed the trusted manifest digest, hashes of `protocol.json` and `results.json`, provenance fields and replay of deterministic fixture assertions. It **does not** prove the source implementation or verifier was uncompromised, or that the fixture came from a live system.

You can independently calculate the manifest digest with Python:

```bash
python -c 'import hashlib,pathlib; p=pathlib.Path(".healthqualify/check-001/manifest.json"); print(hashlib.sha256(p.read_bytes()).hexdigest())'
```

**Important:** calculate and store a digest at creation time; recomputing a digest **after suspected tampering** is not proof of authenticity.

## Interpret the evidence bundle

| Artifact | Review |
| --- | --- |
| `protocol.json` | Full intended test definition, requirements, synthetic data, risk, sources |
| `results.json` | Observed statuses, requirement coverage, build identity, runner version, timestamp |
| `manifest.json` | Hashes of the above, environment and `qualification_approved: false` |
| Externally saved digest | Identifies the exact manifest version you originally trusted |

**Expected built-in demo:** 2 PASS / 5 FAIL. If the run reports all PASS without fixture changes, investigate the source/environment rather than assuming a new release has become compliant.

## Deliberate negative verification

On a **throwaway copy** of the evidence directory, modify one byte of `results.json`. Run `verify` with the original digest. It should return `verified: false` (exit 1). Do not edit the original evidence or change your saved trust anchor to accommodate a tampered bundle.

## Exit codes

| CLI | 0 | 1 | 2 |
| --- | --- | --- | --- |
| `v05cli run` | No FAIL/ERROR/NOT_RUN | At least one incomplete/failed/error test | Invalid protocol/input or execution error |
| `v05cli verify` | Verified | Not verified | Bad input or unexpected read/parse error |
| `cli run-v2` | All coverage/results acceptable to the tool | Gaps or non-PASS outcomes | Input/IO error |
| `cli review-v2` | No human review flag | Human review required | Invalid input |

A **green CI unit suite** verifies a tested portion of repository behavior, not a customer's specific qualification. The **demo runner exiting 1** is correct; CI explicitly expects this case.

## Workspace reports and technical seals

The v0.3 workspace supports `appcli report RUN_UUID DIRECTORY`. It also supports an optional HMAC integrity receipt for a report using `HEALTHQUALIFY_EVIDENCE_KEY` with `appcli seal` and `verify-seal`. Crypto-enabled exports separately support AES-256-GCM encryption and Ed25519 technical receipts. Consult [Security & interoperability](SECURITY_INTEROP_V04.md).

**None** of these constitutes immutable evidence retention, legally valid Part 11 signatures, independent timestamps or clinical validation.

## What to do when things fail

- **Assertion FAIL:** compare expected value to synthetic fixture, investigate requirement, correct test data or implementation through your own workflow, generate **new** evidence.
- **ERROR:** fix the harness or malformed input before drawing conclusions.
- **NOT_RUN / UNCOVERED:** add test coverage and rerun; do not label as PASS.
- **Verify false:** preserve artifacts, compare original trusted digest and file hashes, check whether the runner/verifier changed, and escalate possible tampering.
- **UNKNOWN_IMPACT:** treat all protocol tests as candidates for review; do not approve a release automatically.

## Minimum human evidence review record

For each revision, capture: system ID, intended use, test fixture source, build SHA, environment identity, test author, independent reviewer as required, requirements and risks, protocol digest, outcomes, deviations and retests, external manifest digest, impact findings and final disposition **under a separately controlled QMS**.
