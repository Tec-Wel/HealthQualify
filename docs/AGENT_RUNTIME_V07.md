# HealthQualify v0.7 — Contextual Agent Runtime (Developer Alpha)

**Status:** Synthetic developer implementation only. No PHI, clinical approvals, validated GxP electronic signature, protected WORM storage, public API, model accuracy claim, or hospital integration.

## What's new and why

HealthQualify already has five offline deterministic advisory investigators in `healthqualify/agents.py` and an optional local Ollama/Qwen explanation layer. v0.7 adds an opt-in **local, scoped runtime** that connects those investigators to actual versioned HealthQualify workspace records. The runtime does not need an LLM and never changes authoritative PASS/FAIL, protocols, release decisions or CAPA dispositions.

| Gap | Delivered in v0.7 | Production work still missing |
|---|---|---|
| Real context | Read-only system metadata, protocol version/digest, historical run summaries, test status/evidence references, deviation history | Customer-system integrations and approved per-system data access policies |
| Historical reasoning | Persistent failure, new regression and unresolved-deviation detection across stored runs; cited run/test/deviation identifiers | Correlation to code changes, logs, deployments and qualified root-cause investigation |
| Controlled tools | Authenticated role checks and explicit system grants, redacted outputs, bounded history | Enterprise SSO/MFA, tenant DB isolation, service-to-service auth, secure tool calls |
| Model evaluation | 30 labeled synthetic cases, per-agent TP/FP/FN, deterministic precision/recall, CI artifact | Real Qwen/vLLM inference evaluation, pinned model digest, hallucination/security robustness, latency |
| Proactive triggers | Deduplicated RELEASE_CHANGED, QUALIFICATION_FAILED and COVERAGE_GAP events with review-pending state; explicit one-shot processing | Real event ingestion, trusted event identity, secure scheduled/retry workers and monitoring |
| Multi-user governance | Admin grants, separate author/QA draft decisions (ACKNOWLEDGED / NEEDS_INVESTIGATION / DISMISSED), immutable-by-application observation hashes | Institution IAM, formal reviewer signatures and protected audit retention |
| Regulatory intelligence | Existing source-linked draft-only regulatory profiles are reusable | Controlled official-source retrieval and human-reviewed applicability |
| Observability | Bounded local run history, elapsed time, per-agent counts, model invocation count and review queue | Metrics/trace export, service logs, alerts, distributed observability and model quality monitoring |

## Quickstart for local runtime

Use a **synthetic development database only**. First bootstrap identities and create a system using the existing `healthqualify.appcli`. The v0.7 agent runtime requires that the v0.3 synthetic protocol's `system.id` **exactly equals** the ID of the registered system. Use a copied protocol, not the tracked example.

```bash
python -m healthqualify.appcli --db demo.db init
python -m healthqualify.appcli --db demo.db bootstrap-admin admin_owner
python -m healthqualify.appcli --db demo.db system-add "Synthetic LIS" "Synthetic demonstration" "engineer"

# With admin credentials, grant the engineer and QA access to the system:
python -m healthqualify.agent_runtime_cli_v07 --db demo.db --user admin_owner grant engineer <system-uuid>
python -m healthqualify.agent_runtime_cli_v07 --db demo.db --user admin_owner grant qa_user <system-uuid>

# Copy examples/synthetic_lis_v3/protocol.json and replace system.id with <system-uuid>
python -m healthqualify.agent_runtime_cli_v07 --db demo.db --user engineer \
  analyze <system-uuid> failure-investigation copied-v3-protocol.json

python -m healthqualify.agent_runtime_cli_v07 --db demo.db --user qa_user review-queue <system-uuid>
python -m healthqualify.agent_runtime_cli_v07 --db demo.db --user engineer metrics <system-uuid>
```

The `engineer` and `qa_user` accounts must first be created by an admin using existing identity tooling. Passwords are prompted interactively; no bearer tokens or secrets are passed in command-line arguments. History comes from baselined v0.2 synthetic workspace executions, if any exist. Without prior runs, the runtime explicitly reports `NO_HISTORICAL_RUNS` rather than guessing.

## Local trigger workflow

Trigger events require an authenticated `validator` or `admin` with permission for the system:

```bash
python -m healthqualify.agent_runtime_cli_v07 --db demo.db --user engineer \
  trigger <system-uuid> RELEASE_CHANGED release-demo-001 github-release-v1
```

The result includes a `trigger_id`. Process once using an explicit, reviewed local protocol and changed paths:

```bash
python -m healthqualify.agent_runtime_cli_v07 --db demo.db --user engineer \
  process-trigger <trigger-id> copied-v3-protocol.json --changed healthqualify/healthcare.py
```

Processing writes one **draft advisory observation** to the QA queue. Reusing an event key with different metadata is denied; processing twice is denied. Failed processing is recorded as FAILED rather than automatically approved or silently retried. No trigger modifies CI, deploys code, sends a clinical message or changes test verdicts.

## Review controls

QA reviewers with a grant can select:

- `ACKNOWLEDGED`
- `NEEDS_INVESTIGATION`
- `DISMISSED`

All are **non-approval review dispositions**. Author-reviewer separation is enforced, and reviewed observations cannot be re-reviewed in place. The local SQLite records are not protected from privileged OS administrators; the audit event chain is not an independently trusted regulated record.

## 30-case evaluation

```bash
python -m healthqualify.agent_eval_v07 --out agent-evaluation.json
python -m unittest tests.test_agent_runtime_v07 -v
```

`evaluations/agent_cases.json` includes **30 explicit labels, six synthetic scenarios per agent**, covering mapped/unmapped source paths, uncovered requirements, missing verified evidence and cross-system dependency gaps. Scores are computed against expected finding codes, not inferred from the agent's own labels. CI publishes `healthqualify-agent-deterministic-evaluation` for 30 days.

**Important:** this suite evaluates only deterministic advisory logic. `model_inference_tested=false` and `model_accuracy=null` are deliberate. To measure real Qwen or hosted models, first pin the model digest, execute on approved hardware and evaluate explanatory statements for groundedness, precision, false conclusions, latency, and no modifications to deterministic verdicts.

## Strict agent tool interface

`healthqualify.agent_tools_v07.AgentToolbox` exposes seven approved, **read-only** tools: `system_summary`, `protocol_versions`, `requirement_index`, `recent_runs`, `deviations`, `compare_latest_runs`, and `agent_metrics`. It denies unknown tool names, unauthorized system IDs and unbounded history requests. It does not expose fixture values, raw test observations, arbitrary SQL or operating-system commands.

## Optional local inference acceptance probe

A separate, **explicitly opted-in** probe can invoke a preinstalled local Ollama model against the synthetic labeled cases and preserve its narratives for human grounding review:

```bash
python -m healthqualify.agent_model_probe_v07 \
  --enable-local-ollama --model qwen3:8b --max-cases 30 \
  --out local-model-review.json
```

This script does **not** download a model. Set up a reviewed Ollama instance on loopback and protect network egress independently. Each model response is tagged `DRAFT_UNVERIFIED`; failures remain `MODEL_ERROR`. The deterministic finding digest is checked before and after every call, but a real model's grounding and factuality are **not** automatically scored. The output explicitly contains `model_grounding_score: null` and `human_grounding_review: PENDING`. GitHub CI uses mocks for this pathway, not live Qwen inference.

## Main-branch automated investigations

The additional `.github/workflows/agent-evaluation.yml` runs on every push to `main`. It evaluates 30 gold-label synthetic scenarios and executes all five investigators against the actual `HEAD^..HEAD` file changes. It uploads two draft-only artifacts: `healthqualify-agent-deterministic-evaluation` and `healthqualify-five-agent-main-advisory`. The latter runs on the synthetic LIS fixture with no customer data, secrets, or LLM. It is an automatic developer CI advisory, **not** a real enterprise scheduled monitoring service or release authorization.

## Event and observability boundaries

`agent_triggers` records deduplicated synthetic events; `process-trigger` executes one controlled advisory investigation, never a deployment or test mutation. Admins grant/revoke system scope; QA receives a one-time review decision queue. `metrics` reports local draft count and observed execution latency but not a verified model cost or validated quality score. Enterprise event ingestion, workers and end-to-end monitoring are still separate work.

## Suggested next engineering release

v0.8: properly isolated PostgreSQL organization/service model, identity provider, secure event ingestion, agent tool contracts, production observability, trusted evidence storage and 30-scenario model-inference acceptance testing. A real clinical or regulated launch also requires site-specific intended-use qualification, security/privacy assessment, quality procedures and applicable signature controls.
