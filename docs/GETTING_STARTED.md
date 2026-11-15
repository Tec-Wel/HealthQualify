![Start here documentation](assets/category-start.svg)

[← **Documentation home**](README.md) &nbsp; / &nbsp; **Start here**

# Getting started: your first HealthQualify run

> **What you'll learn:** Clone the repository, execute your first synthetic LIS run, and verify its evidence bundle.

**On this page:** [1. Understand what the demo proves](#1-understand-what-the-demo-proves) · [2. Prepare the machine](#2-prepare-the-machine) · [3. Run the seven-case protocol](#3-run-the-seven-case-protocol) · [4. Inspect evidence, then verify it](#4-inspect-evidence-then-verify-it)

---


**Audience:** first-time developers, healthcare IT testers and validation engineers. **Outcome:** a reproducible offline synthetic run with verifiable technical evidence. **Data:** synthetic only.

## 1. Understand what the demo proves

The included protocol models a synthetic laboratory information system (LIS) exchanging information with an EHR. Seven cases cover a runtime version, patient identifier, laboratory unit, critical result acknowledgment, cross-tenant denial, audit event, and FHIR resource type.

The fixture intentionally violates **five** acceptance criteria. You should see **2 PASS, 5 FAIL**, with `qualification_approved: false`. Finding defects is the **successful demonstration**; a process exit code of 1 is correct for failed assertions.

No hospital server, database, cloud account or AI key is necessary.

## 2. Prepare the machine

Install Git and Python 3.10 or later (Python 3.12 recommended). Verify:

```bash
git --version
python --version
```

If `python` is unavailable, see [Installation](INSTALLATION.md) for Windows `py -3`, macOS `python3`, and virtual environments. From a terminal:

```bash
git clone https://github.com/Tec-Wel/HealthQualify.git
cd HealthQualify
python -m unittest discover -s tests -v
```

All unit tests should pass. These engineering tests do **not** qualify HealthQualify for regulated use.

## 3. Run the seven-case protocol

```bash
python -m healthqualify.v05cli run examples/synthetic_lis_v3/protocol.json --out .healthqualify/first-run
```

The command reports the summary and a 64-character `manifest_sha256`. **Record that digest in an independently controlled location.** The CLI returns 1 because it detected seeded failures. Do not chain this demo to the next command with `&&`.

Files created:

| File | Meaning |
| --- | --- |
| `protocol.json` | Exact original source bytes used by the runner |
| `results.json` | Executed assertions, requirement traceability, statuses and metadata |
| `manifest.json` | SHA-256 digests of artifacts, environment, runner and build provenance |

A second attempt must use a new directory, e.g. `.healthqualify/second-run`; the runner refuses to reuse an existing directory.

## 4. Inspect evidence, then verify it

Open `.healthqualify/first-run/results.json` in your editor, or print it:

```bash
python -m json.tool .healthqualify/first-run/results.json
```

Check that outcomes correspond to the protocol, every requirement has an execution result, and `qualification_approved` remains false.

Use the **exact digest printed in step 3**:

```bash
python -m healthqualify.v05cli verify .healthqualify/first-run --trusted-manifest-sha256 YOUR_SAVED_DIGEST
```

Expected: `{"verified": true}` and exit code 0. An incorrect digest or changed results should produce `{"verified": false}` and exit code 1. Verification also replays the allowlisted synthetic tests using the local implementation; a compromised verifier or modified trust anchor remains out of scope.

## 5. Explore change impact

```bash
python -m healthqualify.v05cli impact examples/synthetic_lis_v3/protocol.json healthqualify/healthcare.py
```

Expected: `REVIEW_REQUIRED` with the mapped HL7 tests. Now try:

```bash
python -m healthqualify.v05cli impact examples/synthetic_lis_v3/protocol.json some/new/module.py
```

Expected: `UNKNOWN_IMPACT`; all existing tests are recommended and `human_review_required` is true. **Neither outcome approves a release.**

## 6. Where to go next

1. Follow [End-to-end workflow](END_TO_END_WORKFLOW.md) for the project lifecycle, including a separate SQLite workspace.
2. Read [User guide](USER_GUIDE.md) to make a safe copy of the JSON protocol for your own **synthetic fixture**.
3. Read [Verification](VERIFICATION_GUIDE.md) to understand evidence trust and failure handling.
4. See [Integration](INTEGRATION_GUIDE.md) for explicitly approved non-production interfaces.

**Stop before real clinical data:** the developer alpha is not approved for PHI, clinical workflow or regulated release. See [Security & limitations](SECURITY_AND_LIMITATIONS.md).

---

### Continue exploring

[end to end workflow](END_TO_END_WORKFLOW.md) · [examples](EXAMPLES.md) · [All guides](README.md) · [Project homepage](../README.md)
