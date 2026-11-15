![Start here documentation](assets/category-start.svg)

[← **Documentation home**](README.md) &nbsp; / &nbsp; **Start here**

# Troubleshooting and diagnostics

> **What you'll learn:** Diagnose common environment, protocol, verification and access-control problems.

**On this page:** [Frequent scenarios](#frequent-scenarios) · [Verify an expected synthetic failure versus a software problem](#verify-an-expected-synthetic-failure-versus-a-software-problem) · [Evidence integrity diagnostic order](#evidence-integrity-diagnostic-order) · [Asking for help](#asking-for-help)

---


Begin with these checks from the repository root:

```bash
python --version
python -m healthqualify.v05cli --help
python -m unittest discover -s tests -v
```

## Frequent scenarios

| Symptom | Explanation | Action |
| --- | --- | --- |
| `No module named healthqualify` | Wrong working directory or interpreter | Go to repository root; activate venv |
| `No module named ...` for optional crypto/DICOM | Missing optional dependencies | `python -m pip install -r requirements-security.txt` |
| Example runner exits 1 | Five seeded LIS tests intentionally FAIL | Inspect result; expected 2 PASS / 5 FAIL |
| Unit test suite fails | Actual engineering regression or environment mismatch | Capture test name, Python version and traceback; open issue with sanitized details |
| `FileExistsError` on evidence export | New-run output directory already exists | Use a fresh `--out` directory |
| `Expected schema_version 0.3` | Wrong protocol track | Use v0.3 for `v05cli`; v0.2 for workspace |
| `Protocol system id must match workspace system id` | Fixture ID not replaced with generated UUID | Copy v0.2 fixture and change `system.id` |
| `Draft execution requires explicit allow_draft` | Workspace draft not baselined | Create separate reviewer baseline event first |
| `verified: false` | Digest mismatch, tampered evidence, invalid replay or provenance | Preserve artifacts and compare against original trusted digest |
| `UNKNOWN_IMPACT` | Changed file not mapped to a test | Treat all tests as review candidates; improve mapping |
| API 403 | Missing/expired session or denied role | Reauthenticate locally; verify role |
| Port 8765 from old instructions | Legacy development API documentation | Secure `appcli serve` defaults to 8877 |
| `readiness` exits 1 | Regulated release intentionally blocked | Review release gates; do not override |
| DICOM inspection can't import pydicom | Optional package missing | Install security dependencies |
| FHIR GET refused | Origin, token, certificate or approval restriction | Confirm approved staging origin, never bypass TLS for remote calls |

## Verify an expected synthetic failure versus a software problem

A successful **unit test** run means code-level tests passed. A successful **demonstration of defect detection** means the synthetic LIS asserts 5 FAIL + 2 PASS, and the CLI returns 1. These results are compatible. The report is not incorrect merely because the fixtures are intentionally bad.

## Evidence integrity diagnostic order

1. Preserve original directory (do not regenerate in place).
2. Check the trusted digest you saved **when the run was created**.
3. Confirm `manifest.json`, `results.json`, and `protocol.json` are present.
4. Run `v05cli verify DIR --trusted-manifest-sha256 DIGEST`.
5. Compare source checkout/verifier version and examine the protocol's build SHA.
6. Escalate any unexplained mismatch rather than re-signing or silently editing evidence.

## Asking for help

Open an [issue](https://github.com/Tec-Wel/HealthQualify/issues) with: current Git commit, OS, Python version, exact command, sanitized protocol fragment, expected versus actual result, traceback with secrets removed, and whether you're running v0.5 standalone, v0.3 workspace, or a one-off adapter. **Never attach PHI, credentials, API tokens or production artifacts.**

See [Security & limitations](SECURITY_AND_LIMITATIONS.md) and [Contributing](../CONTRIBUTING.md).

---

### Continue exploring

[getting started](GETTING_STARTED.md) · [end to end workflow](END_TO_END_WORKFLOW.md) · [All guides](README.md) · [Project homepage](../README.md)
