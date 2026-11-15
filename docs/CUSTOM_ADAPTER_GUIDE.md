![Build & extend documentation](assets/category-build.svg)

[← **Documentation home**](README.md) &nbsp; / &nbsp; **Build & extend**

# Custom check and adapter developer guide

> **What you'll learn:** Learn how to implement reviewed, deterministic synthetic checks without introducing arbitrary execution.

**On this page:** [Choose an extension type](#choose-an-extension-type) · [A fully working example without changing the framework](#a-fully-working-example-without-changing-the-framework) · [Implement a new deterministic check: source-change recipe](#implement-a-new-deterministic-check-source-change-recipe) · [Optional one-off localhost REST assertion](#optional-one-off-localhost-rest-assertion)

---

**Audience:** developers extending HealthQualify for a synthetic engineering use case. **Important:** there is **no public plugin registry or dynamic adapter loading interface** today. Extending the strict runner requires a **reviewed source-code change**, associated tests, and changes to its allowlist. Do not claim arbitrary third-party adapters can be installed from a config file.

## Choose an extension type

| Type | Existing pattern | Data source | Caution |
| --- | --- | --- | --- |
| Deterministic assertion | `healthqualify/healthcare.py` `observe`, `assurance.py` `CHECKS` | Embedded fixture | Only allowlisted, no arbitrary execution |
| Independent bounded REST check | `rest_local.py` | Explicitly authorized localhost `/test/` GET | Not part of the strict protocol runner |
| FHIR staging field check | `fhir_secure.py` | Approved HTTPS GET | Never use PHI or unrestricted host |
| Offline protocol analyzer | `change_graph.py` | Files + explicit component paths | Unknown dependencies must escalate |

## A fully working example without changing the framework

To validate a synthetic application status using the existing `equals` check, make a **copy** of `examples/synthetic_lis_v3/protocol.json` and edit a test fixture/expected value. The minimal protocol specimen in [Configuration](CONFIGURATION.md) includes a `runtime_version: "1.0"` and a matching `equals` test.

```bash
python -m healthqualify.v05cli run my-protocol.json --out .healthqualify/my-adapter-demo
```

Use `v05cli verify` with the printed digest. This tests **synthetic fixture observations**, not a deployed external service.

## Implement a new deterministic check: source-change recipe

This is an **engineering extension recipe**, not an existing plugin API. Suppose an organization wants `starts_with` against a synthetic string:

1. Specify acceptance semantics, input types, exact failure behavior and threat model. Reject non-strings, oversized strings and empty/invalid prefixes.
2. Add an implementation branch in `healthqualify/healthcare.py` under the existing `observe(check, fixture_value, case)` dispatch mechanism.
3. Add the new check name to `healthqualify/assurance.py` `CHECKS`; otherwise protocol validation intentionally rejects it.
4. Confirm strict v0.3 validation delegates to the same safe v0.2 check contract in `protocol_v3.py`; do not weaken unknown-field rejection.
5. Test PASS, FAIL, malformed input, missing fixture and non-ASCII/long input boundaries.
6. Link at least one test to a requirement with a source reference and safe `component_paths`.
7. Confirm results contain correct statuses; a thrown error must not be silently counted PASS.
8. Verify evidence replay and manifest semantics still detect modified results.
9. Add a synthetic fixture and documentation, then open a PR for review.

**Do not** inject Python functions through JSON, execute shell commands described by a protocol, expand arbitrary filesystem access, or permit automatic clinical connections.

## Optional one-off localhost REST assertion

For a server you started yourself on a synthetic `/test/` endpoint:

```bash
python -m healthqualify.v05cli rest-check-local http://127.0.0.1:8000/test/status status '"ready"' --authorize-synthetic
```

There is **no server bundled at that URL**. The implementation refuses public URLs, non-test paths, redirects, writes and missing authorization. It returns only assertion status and redaction metadata; it must not log raw observations.

## Adapter review checklist

- Explicit owner, intended use, authorization and input classification.
- Supported/checkable acceptance criteria and traceability.
- Bounded memory, time, transport and no unexpected network writes.
- Clear outcome states PASS, FAIL, ERROR and NOT_RUN.
- Regression tests for authorization bypass, redirects, malicious data and secret leakage.
- Deterministic replay where supported or a documented evidence limit where not.
- No automated approval, risk downgrading or unreviewed qualified output.

A proposed adapter can be discussed in a GitHub issue first. See [Architecture](DEVELOPER_ARCHITECTURE.md), [Testing](TESTING_AND_CI.md), and [Security model](SECURITY_MODEL.md).

---

### Continue exploring

[developer architecture](DEVELOPER_ARCHITECTURE.md) · [cli reference](CLI_REFERENCE.md) · [All guides](README.md) · [Project homepage](../README.md)
