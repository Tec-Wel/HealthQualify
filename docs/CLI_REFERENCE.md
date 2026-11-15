![Build & extend documentation](assets/category-build.svg)

[← **Documentation home**](README.md) &nbsp; / &nbsp; **Build & extend**

# CLI reference (developer alpha)

> **What you'll learn:** Find the exact synthetic runner, workspace, and quality commands with their inputs and exit behavior.

**On this page:** [v0.5 synthetic and assurance CLI](#v05-synthetic-and-assurance-cli) · [Workspace CLI](#workspace-cli) · [Legacy standalone synthetic CLI](#legacy-standalone-synthetic-cli) · [Exit conventions and safety](#exit-conventions-and-safety)

---

Run from the repository root with Python 3.10+; `python -m MODULE --help` and `python -m MODULE COMMAND --help` are authoritative for flags on your checked-out commit.

## v0.5 synthetic and assurance CLI

Prefix every command below with `python -m healthqualify.v05cli`.

| Command | Arguments | Outcome |
| --- | --- | --- |
| `run` | `PROTOCOL --out NEW_DIRECTORY` | Execute strict v0.3 synthetic JSON and export evidence; 1 for failed/incomplete checks |
| `verify` | `DIRECTORY --trusted-manifest-sha256 DIGEST` | Verify trusted digest, hashes and deterministic replay |
| `impact` | `PROTOCOL CHANGED_FILE [CHANGED_FILE...]` | Advisory file-to-test impact; unknown paths escalate |
| `profile` | `SYSTEM_JSON CONTROLS_JSON --pathway CSA\|IQ-OQ-PQ` | Draft assurance profile; never approval |
| `backup` | `SOURCE_SQLITE NEW_DESTINATION` | Consistent SQLite backup and checksum |
| `backup-verify` | `BACKUP --trusted-sha256 DIGEST` | Check backup hash plus SQLite integrity |
| `backup-restore` | `BACKUP NEW_DB --trusted-sha256 DIGEST` | Restore into a new path only |
| `rest-check-local` | `URL FIELD EXPECTED_JSON --authorize-synthetic` | Authorized loopback synthetic JSON GET field assertion |
| `benchmark` | `V2_PROTOCOL` | Internal fixture timing and outcomes; no third-party comparison |

`--out`, `--trusted-manifest-sha256` and `--trusted-sha256` are not interchangeable. A trusted digest must be preserved outside the mutable artifact.

## Workspace CLI

Global option: `python -m healthqualify.appcli --db PATH COMMAND`. Some commands ignore the DB because they are stateless helper functions.

| Command | Inputs | Purpose |
| --- | --- | --- |
| `init` | none | Create/open local workspace |
| `system-add` | `NAME INTENDED_USE OWNER` | Register system, print UUID |
| `systems`, `protocols`, `runs`, `deviations`, `audit` | none | List corresponding local records |
| `protocol-add` | `SYSTEM_UUID V2_JSON AUTHOR` | Store v0.2 draft protocol |
| `baseline` | `PROTOCOL_UUID REVIEWER RATIONALE` | Separate-author reviewer event, **not** legal signature |
| `run` | `PROTOCOL_UUID ACTOR` | Execute baselined v0.2 protocol |
| `report` | `RUN_UUID DIRECTORY` | Export technical report |
| `frameworks`, `agents`, `readiness` | none | Regulatory catalog, agent roles, release blockers |
| `bootstrap-admin` | `USERNAME` | Prompt securely for initial password |
| `create-user` | `ADMIN_USERNAME USERNAME ROLE` | Prompt for admin and new user passwords |
| `serve` | `--host 127.0.0.1 --port 8877` (defaults) | Authenticated loopback API |
| `draft-urs` | `SYSTEM_JSON NEEDS_JSON` | Draft URS suggestions |
| `risk-plan` | `SYSTEM_JSON FRAMEWORKS_JSON CRITICALITY` | Draft risk/assurance plan |
| `applicability` | `SYSTEM_JSON DECISIONS_JSON` | Evaluate explicit framework decisions |
| `regulation-diff` | `OLD_TEXT NEW_TEXT` | Compare operator-provided text |
| `regwatch-capture` | `FRAMEWORK TEXT_FILE` | Record operator-supplied snapshot |
| `modelqual` | `ROWS_JSON` | Offline classification metrics |
| `draft-agent` | `ROLE MODEL TEXT_FILE --allow-local-ai` | Optional local Ollama draft |
| `fhir-check-local` | `URL PATH EXPECTED_JSON --allow-local-http` | Read-only loopback FHIR check |
| `fhir-check-approved` | `URL FIELD EXPECTED_JSON --authorize-read-only` | Approved-origin HTTPS FHIR read |
| `hl7-mllp-inspect` | `FILE --authorize-synthetic` | Inspect synthetic captured frame |
| `dicom-synthetic` | `FILE --authorize-synthetic` | Inspect offline synthetic metadata |
| `device-snapshot` | `FILE --authorize-synthetic` | Validate passive synthetic telemetry |
| `seal`, `verify-seal` | `DIRECTORY` | Optional shared-secret technical receipt |
| `protect-export` | `SOURCE DESTINATION` | AES-GCM and Ed25519 technical export |
| `verify-protected` | `DIRECTORY` | Verify protected archive against trusted public key |
| `review-attest` | `USERNAME PROTOCOL_UUID MEANING RATIONALE` | Password reauthentication technical review receipt |

## Legacy standalone synthetic CLI

Prefix with `python -m healthqualify.cli`:

`run PROTOCOL --out DIR`, `verify DIR`, `validate-v2 PROTOCOL`, `run-v2 PROTOCOL --out DIR`, `verify-v2 DIR [--trusted-manifest-sha256 DIGEST]`, `review-v2 BEFORE_JSON AFTER_JSON`.

## Exit conventions and safety

For synthetic runners: **0** generally indicates all relevant checks passed, **1** indicates failed/incomplete assertions or verification mismatch, **2** input/runtime errors. Some helper commands return 0 after producing an advisory, not approval. The `appcli readiness` command deliberately returns 1 while release gates remain unmet. Always inspect JSON, not merely process exit status.

For payload/schema detail see [Configuration](CONFIGURATION.md), [Integration](INTEGRATION_GUIDE.md), and [Verification](VERIFICATION_GUIDE.md).

---

### Continue exploring

[developer architecture](DEVELOPER_ARCHITECTURE.md) · [testing and ci](TESTING_AND_CI.md) · [All guides](README.md) · [Project homepage](../README.md)
