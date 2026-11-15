# Configuration and protocol authoring

## No hidden global config for the core runner

The strict v0.5 runner reads the JSON protocol path supplied on the command line and writes a **new** evidence output directory. It runs offline, reads embedded fixtures and does not require external keys or a central service.

## Strict v0.3 protocol structure

Start by copying `examples/synthetic_lis_v3/protocol.json`, which contains all major fields. The following is a **minimal illustrative draft fixture**, not a healthcare qualification approval:

```json
{
  "schema_version": "0.3",
  "qualification_state": "draft",
  "system": {
    "id": "SYNTH-APP-001",
    "version": "1.0",
    "intended_use": "Offline synthetic demonstration",
    "environment": "synthetic",
    "build_sha": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
  },
  "requirements": [
    {
      "id": "URS-001",
      "risk": "low",
      "acceptance_basis": "Fictional release specification: version equals 1.0",
      "source_id": "SYNTH-SPEC"
    }
  ],
  "fixtures": { "runtime_version": "1.0" },
  "tests": [
    {
      "id": "IQ-001",
      "phase": "IQ",
      "requirement_ids": ["URS-001"],
      "check": "equals",
      "fixture": "runtime_version",
      "expected": "1.0",
      "component_paths": ["src/version.py"]
    }
  ],
  "execution_policy": {
    "network": false,
    "destructive": false,
    "allow_ai": false,
    "data_classification": "synthetic",
    "runner_version": "0.5.0a0"
  },
  "source_references": {
    "SYNTH-SPEC": "Fictional system acceptance criteria for training"
  },
  "approval_reference": null
}
```

A 40-character `build_sha` is required; the all-`a` string above is **demo-only**, not evidence of a real build. For your own fixture, replace it with the exact tested source revision. Paths under `component_paths` are **relative POSIX-style repository paths**; no `../`, absolute paths, or backslashes.

### Field contract and guardrails

- `schema_version` **must be `"0.3"`** for `v05cli`; `qualification_state` must remain `"draft"`.
- `system` identifies intended use, version, test environment and full 40-character build identifier.
- `requirements` need unique identifiers, risk, nonempty acceptance basis and an existing `source_id` in the registry.
- `tests` reference requirements and allowlisted deterministic checks; unsupported/extra keys are rejected.
- `fixtures` are provided **inside the protocol**, never read from a hospital production system by this runner.
- `execution_policy.network`, `destructive`, and `allow_ai` must all be **false**. Data classification must be `synthetic` or `public`.
- `approval_reference` must remain `null`. This alpha cannot claim formal approval.
- Each test declares at least one safe `component_paths` entry for conservative change impact.

The v0.3 validator delegates detailed allowable `check`, `phase`, `risk`, and fixture type rules to the existing v0.2 assertion schema. Consult `healthqualify/assurance.py` and the actual fixture rather than inventing new check names. Examples used now: `equals`, `present`, `hl7_field_equals`, `role_denied`, and `fhir_field_equals`.

## Command and environment configuration

| Variable | Used for | Guidance |
| --- | --- | --- |
| `HEALTHQUALIFY_FHIR_ORIGIN` | Approved read-only FHIR exact origin | Restricted approved non-production HTTPS origin |
| `HEALTHQUALIFY_FHIR_BEARER` | FHIR read-only bearer token | Inject at runtime; do not commit |
| `HEALTHQUALIFY_EVIDENCE_KEY` | Legacy HMAC receipt | External secret; not a legal signature |
| `HEALTHQUALIFY_AES_KEY_B64` | Protected export encryption | Base64 key, manage securely |
| `HEALTHQUALIFY_SIGN_SEED_B64` | Technical signature seed | Keep private; not a regulated approval |
| `HEALTHQUALIFY_PUBLIC_KEY_B64` | Protected export verification | Obtain from independently trusted source |
| `HEALTHQUALIFY_API_TOKEN` | Legacy unprotected development API | **Not** authentication for the current secure `appcli serve` |

**Do not confuse** legacy README examples referring to port 8765 or an API token with today's `appcli serve`. The current secure API uses password bootstrap, login sessions and defaults to **port 8877** on loopback.

## Workspace compatibility

`appcli protocol-add` currently calls the **v0.2** validator and requires `payload.system.id` equal to the UUID from `system-add`. The standalone v0.5 v0.3 JSON and workspace v0.2 JSON should be maintained separately. See [End-to-end workflow](END_TO_END_WORKFLOW.md).

## Project hygiene

Commit reviewed template protocols and documentation; avoid committing `.healthqualify/` generated evidence, credentials, report archives or local SQLite DB files. Store trusted digests independently. For deployment and data boundaries, see [Security & limitations](SECURITY_AND_LIMITATIONS.md).
