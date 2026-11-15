# HealthQualify — Five Local Advisory Agents

**Status:** Developer-alpha feature; synthetic v0.3 protocols only. **Not** a validated GxP application, FDA certification, Part 11 electronic signature, protected audit trail, or release approval mechanism.

The agents are **read-only investigators**. They do not execute qualification tests, change authoritative PASS/FAIL, approve protocols, resolve CAPAs, sign releases, or connect to clinical systems. By default they invoke **no LLM** and make **no network calls**. An optional local Ollama model can explain the same fixed deterministic findings.

## Quick start (Python 3.10+)

From the repository root:

```bash
python -m unittest discover -s tests -v
python -m healthqualify.agentcli release-impact examples/synthetic_lis_v3/protocol.json --changed healthqualify/healthcare.py
python -m healthqualify.agentcli gap-hunter examples/synthetic_lis_v3/protocol.json
python -m healthqualify.agentcli qa-readiness examples/synthetic_lis_v3/protocol.json
python -m healthqualify.agentcli failure-investigation examples/synthetic_lis_v3/protocol.json
python -m healthqualify.agentcli dependency-investigator examples/synthetic_lis_v3/protocol.json --registry examples/agents/dependencies.json --changed healthqualify/healthcare.py
```

These commands analyze **source-linked synthetic data**. No model installation is needed for deterministic findings. They do not require secrets or cloud credentials.

## Verify actual synthetic test evidence

Generate a separate v0.3 synthetic evidence directory:

```bash
python -m healthqualify.v05cli run examples/synthetic_lis_v3/protocol.json --out .healthqualify/demo-run
```

This deliberately contains seeded FAIL results, so an exit code of **1 is expected**. The output reports `manifest_sha256`; copy its exact value into the following command using a trusted copy **stored outside the evidence directory**:

```bash
python -m healthqualify.agentcli failure-investigation examples/synthetic_lis_v3/protocol.json --evidence-dir .healthqualify/demo-run --trusted-manifest-sha256 YOUR_TRUSTED_SHA256
python -m healthqualify.agentcli qa-readiness examples/synthetic_lis_v3/protocol.json --evidence-dir .healthqualify/demo-run --trusted-manifest-sha256 YOUR_TRUSTED_SHA256
python -m healthqualify.agentcli gap-hunter examples/synthetic_lis_v3/protocol.json --evidence-dir .healthqualify/demo-run --trusted-manifest-sha256 YOUR_TRUSTED_SHA256
```

A missing or mismatched trusted digest **stops** analysis. Without verified evidence, gap and readiness agents explicitly report that execution cannot be established.

## Agent details

| Agent | Required input | Deterministic output | Boundaries |
|---|---|---|---|
| `release-impact` | v0.3 protocol, explicit changed paths | Existing conservative change-to-test graph, unknown paths | Cannot declare release qualified |
| `gap-hunter` | v0.3 protocol, optional verified evidence | Uncovered requirements, missing/non-PASS execution | Does not infer unspecified negative-test coverage |
| `failure-investigation` | v0.3 protocol and preferably verified evidence | Non-PASS test IDs with evidence references | No root-cause determination or CAPA closure |
| `qa-readiness` | v0.3 protocol, optional verified evidence | Blockers and missing records | Always REVIEW_BLOCKED for this synthetic developer alpha |
| `dependency-investigator` | v0.3 protocol, explicit changed paths, local registry | Mapped systems and unknown components | Registry completeness is a human responsibility |

**Important:** The alpha protocol has no formally approved negative-test classification, time-aware execution-baseline registry, or qualified approval/e-signature implementation. Agents must not claim to detect what the underlying data cannot establish. Extend schemas and authorization after independent review before regulated use.

## Optional local Qwen via Ollama

Install Ollama locally and fetch your reviewed model while connected:

```bash
ollama pull qwen3:8b
ollama list
```

Start Ollama listening only on `127.0.0.1:11434`. Disable Ollama cloud capabilities and block unapproved outbound traffic using host firewall or VM isolation. Then, **only with synthetic inputs**:

```bash
python -m healthqualify.agentcli gap-hunter examples/synthetic_lis_v3/protocol.json --ollama --model qwen3:8b
```

The model adds `model_explanation` and **cannot rewrite** `summary`, `findings`, `qualification_approved`, or `evidence`. It sees the bounded list of deterministic findings, not raw fixtures or patient data. Ollama invocation uses the existing `healthqualify.ai.local_draft` allowlisted loopback endpoint. A model failure returns a CLI error; it is never treated as passing qualification. The provider request is explicitly opt-in and default-off.

## Output contract

`HQ-AGENT-DRAFT-0.1` JSON reports contain `agent`, `system_id`, `protocol_sha256`, `status=DRAFT_UNVERIFIED`, `qualification_approved=false`, `evidence=false`, `human_review_required=true`, `summary`, `findings`, and optional `model_explanation`. Findings carry `code`, `severity`, `message`, and `source_refs`.

To write a **new** report file without overwriting one:

```bash
python -m healthqualify.agentcli gap-hunter examples/synthetic_lis_v3/protocol.json --out draft-gaps.json
```

The CLI errors if the output file already exists. Store copies and their hashes according to your organization's approved record controls. These agent reports are **not** authoritative qualification evidence.

## Dependency registry schema

`examples/agents/dependencies.json` illustrates a registry:

```json
{"systems":[{"id":"LIS","components":["healthqualify/healthcare.py"]}]}
```

Components are repository-relative path prefixes. Missing components are reported as `UNKNOWN_DEPENDENCY`; do not treat an incomplete registry as proof of no other impacts.

## User workflow

1. **Choose a synthetic protocol** and check version, source references, component links, and expected behavior.
2. **Run release-impact** on explicit local Git change paths (a GitHub connection is not required).
3. **Run gap-hunter** to identify unmapped requirements and note any missing verified execution.
4. **Execute a separate, controlled synthetic protocol** with `healthqualify.v05cli run`.
5. **Independently retain the manifest digest**, then run the failure and readiness agents against verified evidence.
6. **Run dependency-investigator** using an approved local system registry.
7. **Review each finding** with qualified personnel. Draft explanations do not alter deterministic results.
8. **Retain the report** under organizational policies; do not use this alpha as a system of regulated record.

## Security and limitations

- Input protocol is bounded to a 1 MiB file and strictly validated as synthetic v0.3.
- No arbitrary model tool calling, shell execution, test execution, file edits, cloud APIs or remote URLs.
- LLM prompt contains only summary findings; source documents are **not trusted instructions**.
- Filesystem permissions, endpoint isolation, backup protection, identity and audit control remain the deployer's responsibility.
- Trusted evidence SHA-256 must be independently stored. A self-consistent artifact with no external trust anchor is not proof of authenticity.
- This first release is a CLI, **not yet integrated into the authenticated UI/API**. For multiuser usage, authentication, per-system authorization, rate limits, retention and append-only audit controls must be implemented first.
- Time-aware comparison against historical qualified baselines, predictive root-cause investigation, approvals and live integration are future features.

## Acceptance tests

```bash
python -m unittest tests.test_agents -v
python -m unittest discover -s tests -v
```

Tests cover all agents, mapped and unknown changes, missing evidence, invalid hashes, duplicate systems, path traversal, AI default-off behavior, and the inability of a mocked LLM to change readiness. Passing tests confirms developer behavior, **not** production qualification or FDA compliance.
