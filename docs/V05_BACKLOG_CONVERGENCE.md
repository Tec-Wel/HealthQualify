![Project reference documentation](assets/category-reference.svg)

[← **Documentation home**](README.md) &nbsp; / &nbsp; **Project reference**

# HealthQualify v0.5 — Backlog Convergence

> **What you'll learn:** Read technical v0.5 evidence, backup, impact and qualification convergence details.

**On this page:** [Nine-issue implementation matrix](#nine-issue-implementation-matrix) · [Developer commands](#developer-commands) · [Branch cleanup policy](#branch-cleanup-policy) · [Safety limitations](#safety-limitations)

---


**Release classification:** technical developer alpha. Not suitable for PHI, hospital production, clinical decision support or regulated electronic-record approval. No IQ/OQ/PQ or CSA pathway is automatically certified.

## Nine-issue implementation matrix

| Issue | Progress implemented in v0.5 | Remaining acceptance and external work |
|---|---|---|
| #1 Protocols | Strict v0.3 schema: source registry, required risk linkage, full build identifier, runner version, safe component paths, explicit offline/synthetic execution policy. Previous v0.2 baseline workflow retained. | Formal approval schema, migration, verified external document provenance and tool validation |
| #2 Healthcare adapters | Existing restricted FHIR GET, synthetic HL7 and local DICOM/device checks retained, with v0.3 synthetic HL7/FHIR pack. | Real staged authenticated HL7/MLLP workflows, FHIR profiles, DICOMweb/PACS and vendor test harness |
| #3 EvidenceChain | New v0.3 evidence receipts bind exact protocol bytes, canonical protocol digest, runner version, build, environment, results and independent manifest digest. Existing encrypted/signed technical exports retained. | Trusted timestamping, remote protected store, key lifecycle, retention and recovery |
| #4 Traceability/CAPA | Existing requirement-to-result graph, persistent deviations plus newly tracked CAPA root cause, correction, effectiveness criteria, independent reviewer and same-system baselined retest; deviation closes with CAPA transaction. | Quality-system workflow, assignment/SLA, external reviewer signatures and validated records |
| #5 Regulatory/CSA | Draft-only, source-linked applicable-framework mapping with distinct guidance/regulation/standard classification and CSA or IQ/OQ/PQ testing modes. | Official content version lifecycle, legal applicability review, licensed GAMP controls |
| #6 Change impact | Version-aware conservative component paths -> tests, unknown changes trigger all current tests and human review. | CI webhook integration, dependency discovery, manual disposition, release orchestration |
| #7 Optional AI | Provider-neutral draft interface with strict no-approval/no-evidence contract, disabled default, local Ollama adapter; existing offline ModelQual metrics. | vLLM and hosted provider adapters, security benchmarking, model governance |
| #8 Deployment/governance | Consistent SQLite backup, integrity and trusted checksum validation; existing RBAC/secure loopback service and encrypted exports. | Cloud deployment with PostgreSQL, TLS, SSO/MFA, restore drills, WORM evidence, pentest |
| #9 Benchmarks | Reproducible internal seeded-LIS benchmark harness with wall time and outcomes and explicit *comparison not run*. | Equal-input external baselines with conventional qualification scripts, traceability tools and pytest; repeat trials and publish measured comparisons |

**All nine original issues remain open unless their full original acceptance criteria are independently met. A CI success does not mean they are completed.**

## Developer commands

Python 3.12 suggested; v0.5 tools remain stdlib-only:

```bash
python -m unittest discover -s tests -v

# Deliberately seeded five synthetic defects: exit code 1 is expected.
python -m healthqualify.v05cli run \
  examples/synthetic_lis_v3/protocol.json --out .healthqualify/v05-run

# Hash the manifest independently, save the result in trusted storage.
python -c 'import hashlib,pathlib;print(hashlib.sha256(pathlib.Path(".healthqualify/v05-run/manifest.json").read_bytes()).hexdigest())'
python -m healthqualify.v05cli verify .healthqualify/v05-run \
  --trusted-manifest-sha256 <saved-digest>

# Conservative code-to-test impact review.
python -m healthqualify.v05cli impact \
  examples/synthetic_lis_v3/protocol.json healthqualify/healthcare.py

# Internal fixture benchmark ONLY (no competitor scores).
python -m healthqualify.v05cli benchmark examples/synthetic_lis_v2/protocol.json

# Database consistent backup from local test data.
python -m healthqualify.v05cli backup healthqualify.db backup.db
python -m healthqualify.v05cli backup-verify backup.db --trusted-sha256 <saved-digest>
```

## Branch cleanup policy

The three previous feature branches were already squash-merged in PRs #10, #11, #12. A narrowly scoped GitHub Actions workflow `.github/workflows/prune-merged.yml` is set to run after a **successful main-branch test workflow**. It deletes only those named feature branches, only when (1) the corresponding PR is confirmed merged into `main`, (2) GitHub still reports the exact known branch head SHA, and (3) no open PR references the branch.

If the workflow lacks permission, or if the branch has moved, it must fail or preserve the branch. Never rewrite or remerge the old feature branches. The clean-up job does not act on `main` or newer feature branches.

## Safety limitations

- v0.3 protocol receipts are **technical evidence**, not qualified electronic records.
- Manifest hashes require a separately trusted reference.
- Backup files are unencrypted. Use only synthetic data and protect backup files externally.
- The code-to-test map can omit hidden dependencies; unknown paths cause a fail-closed review.
- External API and clinical test execution must be separately authorized, monitored and isolated.
- CAPA closure is a software workflow record, not a legally sufficient regulated quality disposition.
- The synthetic benchmark **does not demonstrate superior performance** to other tools.

---

### Continue exploring

[release status](RELEASE_STATUS.md) · [roadmap](ROADMAP.md) · [All guides](README.md) · [Project homepage](../README.md)
