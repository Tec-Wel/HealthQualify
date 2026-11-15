![AI investigators documentation](assets/category-agents.svg)

[← **Documentation home**](README.md) &nbsp; / &nbsp; **AI investigators**

# HealthQualify — Local Five-Agent Dashboard and Orchestration

> **What you'll learn:** Configure the single-user loopback dashboard and understand agent orchestration and its safety boundaries.

**On this page:** [What is included](#what-is-included) · [Quick start — without an AI model](#quick-start-without-an-ai-model) · [Local dashboard](#local-dashboard) · [Architecture](#architecture)

---

> **Developer alpha only.** All five investigators operate on approved local synthetic v0.3 protocol inputs. These workflows are not production-qualified GxP software or electronic records/signatures. No PHI or production systems. No agent can approve a protocol or modify PASS/FAIL.

## What is included

- Five agents: Release Impact Investigator, Qualification Gap Hunter, Failure Investigation Copilot, QA Evidence Readiness, and Cross-System Dependency Investigator.
- An offline deterministic analysis layer backed by existing HealthQualify protocol and evidence functions.
- Optional, **explicitly opt-in** local Ollama/Qwen explanations; no hosted AI calls.
- A local single-user web dashboard, agent run history and state transitions in a separate SQLite database.
- A serial "run all five" orchestration flow; no uncontrolled autonomous tool loops.
- An append-only-by-application hash-chained development event log. **Not immutable evidence.** Store chain-head digests in separately controlled storage if integrity matters.

## Quick start — without an AI model

Install Python 3.10+ and Git, then:

```bash
git clone https://github.com/Tec-Wel/HealthQualify.git
cd HealthQualify
git checkout feature/local-five-advisory-agents
python -m unittest tests.test_agents tests.test_agent_orchestrator -v
```

Run all agents from the command line:

```bash
python -c "from healthqualify.agent_orchestrator import AgentHistory; h=AgentHistory('agents-demo.db'); print([(x['agent'],x['state']) for x in h.run_all('demo_user','examples/synthetic_lis_v3/protocol.json',changed_files=['healthqualify/healthcare.py'],registry_path='examples/agents/dependencies.json')['jobs']]); h.close()"
```

For individual agents and verified synthetic execution evidence, see [AI_AGENTS_GUIDE.md](AI_AGENTS_GUIDE.md).

## Local dashboard

Generate a random **minimum 32-character** secret with Python and set it as a local environment variable. For example, on Linux/macOS:

```bash
export HEALTHQUALIFY_AGENT_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(40))')"
python -m healthqualify.agent_dashboard
```

On PowerShell:

```powershell
$env:HEALTHQUALIFY_AGENT_TOKEN = python -c "import secrets; print(secrets.token_urlsafe(40))"
python -m healthqualify.agent_dashboard
```

Visit **http://127.0.0.1:8899**. Enter your locally generated token, click **Load history**, and run an agent or **Run all five agents**.

The page never sends your token to any external server; it uses same-origin localhost API calls. The token is stored in page memory, not browser local storage. The dashboard is bound to `127.0.0.1` and uses a single-threaded server because the SQLite connection is local and single-process.

The dashboard reads configured synthetic sample files and uses a configured set of changed paths. It accepts **no arbitrary filesystem paths** from the browser. API requests require a bearer token; agent invocation has a bounded JSON body. This is a single-user development token, not enterprise SSO, MFA, per-system RBAC or formal QA review authorization.

### Enable local Qwen explanations

First install Ollama and download a reviewed local Qwen model. Bind Ollama to `127.0.0.1:11434`; disable its cloud features and independently enforce outbound firewall restrictions.

```bash
ollama pull qwen3:8b
ollama list
python -m healthqualify.agent_dashboard --allow-ollama
```

The dashboard's **Request optional local Qwen explanation** checkbox opt-ins per run. Both the server flag and checkbox must be enabled. With the checkbox off, no model is called. A local model failure records FAILED, not a passing outcome. The AI sees the summary and deterministic findings only and cannot rewrite them.

### Configure alternative synthetic inputs

```bash
python -m healthqualify.agent_dashboard \
  --db .healthqualify/agent-history.db \
  --protocol examples/synthetic_lis_v3/protocol.json \
  --registry examples/agents/dependencies.json \
  --changed healthqualify/healthcare.py \
  --port 8899
```

Only pass pre-reviewed, non-PHI local files. The dashboard does not execute arbitrary source code or fetch live repositories. For execution-dependent findings, use the individual agent CLI with an independently trusted manifest hash as described in [AI_AGENTS_GUIDE.md](AI_AGENTS_GUIDE.md); the dashboard defaults to reporting missing verified execution.

## Architecture

```text
Local browser 127.0.0.1:8899
  -> token-guarded single-user HTTP handler
  -> serial local AgentHistory orchestration
  -> five deterministic investigators
  -> source-linked DRAFT_UNVERIFIED JSON
  -> optional Ollama 127.0.0.1:11434 explanation
  -> local SQLite development history
```

The orchestration database stores state transitions (QUEUED, ANALYZING, DRAFT, FAILED), reports, and event hashes. Hash chaining requires an external trusted anchor to detect full-history replacement. Local SQLite can be modified by a privileged operator; it is not qualified audit/WORM storage.

## How each agent works

1. **Release Impact:** Reuses conservative `plan_requalification` mappings and flags unmapped paths.
2. **Gap Hunter:** Computes requirement-to-test coverage; without separately verified evidence reports no verified execution. Does not invent negative-test classifications.
3. **Failure Investigation:** Reads verified execution results and flags non-PASS tests for manual investigation. No root cause is asserted as fact.
4. **QA Evidence Readiness:** Reviews source-linked gaps and evidence availability. Synthetic developer-alpha outputs are **always REVIEW_BLOCKED**, never FDA approval.
5. **Cross-System Dependencies:** Resolves changed components against an explicit local system registry; missing matches are flagged.

## Run the tests

```bash
python -m unittest tests.test_agents tests.test_agent_orchestrator -v
python -m unittest discover -s tests -v
```

The tests cover all five agents, run history, failure-state persistence, unknown change mapping, evidence digest mismatch, default-off inference and prohibition of approval.

## FDA-regulated production use: NOT COMPLETE

Before using HealthQualify as a regulated system of record or generating regulated approval decisions, an organization must establish intended use, risk classification, requirements, documented assurance/validation, SSO/MFA and segregation of duties where applicable, qualified e-signatures, protected and immutable record retention, independent trusted timestamps, approved change control, backups and restore tests, security assessment, model governance, SOPs, and independent QA approval. The open-source synthetic alpha currently does not deliver these controls.

Passing CI and successful Qwen inference are **engineering evidence**, not FDA qualification.

## Real Qwen inference acceptance procedure

CI can verify agent logic without Ollama. Real inference requires an Ollama runtime with the approved model actually downloaded, which is **not included in GitHub-hosted unit tests**.

1. Confirm `ollama list` includes the intended exact model; record its immutable digest.
2. Start the dashboard with `--allow-ollama`.
3. Run every agent with local inference selected.
4. Confirm each report has `model_explanation.status=DRAFT_UNVERIFIED` and deterministic findings are unchanged.
5. Disconnect external networking and repeat.
6. Remove or stop Ollama and confirm failed model jobs are recorded as FAILED.
7. Retain redacted outputs and system diagnostics for engineering review.

Do not record this test as passed until someone actually completes it on approved hardware.

---

### Continue exploring

[ai agents guide](AI_AGENTS_GUIDE.md) · [feature matrix](FEATURE_MATRIX.md) · [All guides](README.md) · [Project homepage](../README.md)
