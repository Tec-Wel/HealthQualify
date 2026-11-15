# Testing and continuous integration

## Test philosophy

HealthQualify's test suite verifies **developer-alpha behavior**, not the qualification of a customer's healthcare deployment. Every feature must demonstrate failure handling, input validation, safe defaults and evidence integrity. Green CI is necessary for accepting changes but does **not** prove compliance.

## Local commands

From repository root, Python 3.12 recommended:

```bash
python -m pip install -r requirements-security.txt
python -m unittest discover -s tests -v
```

The internal equal-input benchmark additionally requires:

```bash
python -m pip install 'pytest>=8,<10'
python -m benchmarks.compare --repetitions 3 --out benchmark-results.json
```

The benchmark measures synthetic executor behavior, not external superiority or human productivity. See [v0.6 benchmark](QUALITY_RELEASE_BENCHMARK_V06.md).

## Test suites by responsibility

| Path or suite | Focus |
| --- | --- |
| `tests/test_engine.py`, `tests/test_assurance_v2.py` | Deterministic assertion outcomes, source coverage, invalid tests |
| `tests/test_v05.py`, `tests/test_ci_impact.py` | Strict schema, replay/tamper, change impact and Git SHA inputs |
| `tests/test_product_v03.py` | SQLite baseline and lifecycle |
| `tests/test_rest_local.py`, `tests/test_rest_trace_restore.py` | Local read-only REST constraints, redaction, evidence links, restore |
| `tests/test_security_api_v04.py`, `tests/test_security_interop_v04.py` | Identity, API restrictions, crypto and healthcare adapter boundaries |
| `tests/test_capa_v05.py`, `tests/test_quality_workflows_v06.py` | Review/CAPA/release workflow checks |
| `tests/test_benchmark_v06.py` | Equal-input benchmark contract |

## Expected negative qualification runs

```bash
python -m healthqualify.v05cli run examples/synthetic_lis_v3/protocol.json --out .healthqualify/ci-demo-001
```

This intentionally returns **exit 1**, **5 FAIL and 2 PASS**. Treat a genuine unit-test failure separately from a qualification demo deliberately finding defects. The GitHub Actions workflow encodes the expected exit status and validates evidence.

## GitHub workflow map

- `.github/workflows/tests.yml`: Python dependencies, unit tests and deterministic seeded qualification demos; PR impact advisory reports conservative test recommendations.
- `.github/workflows/benchmark.yml`: reproducible local synthetic comparison; does not establish superiority.
- `.github/workflows/release-qualification.yml`: tag/release-triggered source impact advisory with human review required, not deployment authorization.
- `.github/workflows/prune-merged.yml`: narrowly scoped historic branch cleanup under preconditions; review before expanding scope.

## Author checklist for every PR

1. Run unit tests and include the exact result/commit.
2. Add at least one negative or error-case test for changed logic.
3. Check outputs for raw sensitive observations and secrets.
4. Verify evidence replay with an independently saved digest where applicable.
5. Check mapped and unmapped source changes trigger conservative recommendations.
6. Run documentation links and copy/paste examples relevant to the change.
7. Ensure no new CLI help claims an unimplemented feature.
8. Preserve human approval gates; never auto-approve regulated use.

## Triage failures

Identify **which** step failed (install, unit test, demo execution, expected count, verification, PR impact). Inspect GitHub Actions logs with secrets removed. For a reproducible issue, provide version, OS, Python interpreter, branch SHA, command, sanitized JSON and expected/actual result.

See [Troubleshooting](TROUBLESHOOTING.md) and [Contributing](../CONTRIBUTING.md).
