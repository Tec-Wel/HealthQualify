![Project reference documentation](assets/category-reference.svg)

[← **Documentation home**](README.md) &nbsp; / &nbsp; **Project reference**

# HealthQualify architecture and trust boundaries

> **What you'll learn:** Understand the original platform model, execution safety constraints, and trust boundaries.

**On this page:** [Model](#model) · [Execution safety](#execution-safety) · [Trust model](#trust-model) · [Deployment evolution](#deployment-evolution)

---

## Model
- **Protocol:** versioned machine-readable requirements, test definitions, expected outcomes, environment and approval reference.
- **Runner:** a small deterministic execution engine. Only allowlisted built-in checks in the alpha; no arbitrary shell or AI-generated code execution.
- **EvidenceChain:** a directory with copied protocol, results, and manifest. Each artifact's SHA-256 can be verified locally.
- **Traceability:** for every requirement identify linked tests, recorded statuses and uncovered/gap cases. Merely declaring a test is not proof it ran.
- **Quality workflow (planned):** approved protocol baselines, deviations, linked retests, quality reviews, append-only event history and appropriate retention.

## Execution safety
1. Explicit target environment selection, authority and test-data constraints.
2. Default read-only and synthetic data; destructive, failure-injection and load tests are isolated and separately approved.
3. Workloads have timeouts, resource limits and network/credential boundaries.
4. A failed runner, missing evidence or unsupported check is not PASS.
5. Approved requirement or acceptance criteria edits produce a new version requiring review.
6. Test output is a **technical observation**. Final qualification is a human decision under the organization's quality system.

## Trust model
SHA-256 detects changes when compared to a known trusted reference; it does not prevent deletion or rewriting. For a regulated multi-user deployment add signed attestations, trusted timestamps, identity enforcement, access controls, protected storage, audit log, backup/recovery, retention and qualified e-signatures where applicable. The platform itself must be assured for its intended regulated use.

## Deployment evolution
- Alpha: Python CLI + JSON protocol + local filesystem evidence.
- Beta: Python package, SQLite, healthcare-specific adapters, JSON/HTML reports, CI.
- Service: FastAPI, PostgreSQL, worker queue, React UI, S3-compatible artifact store; Docker Compose for local/EC2/GCP/Azure/on-prem.
- AI: adapter interface only, off by default; Ollama/vLLM or approved hosted API for **draft suggestions**.

## Control plane and test plane
Separate control-plane state (approved protocols, policies, reviewers and metadata) from test workers that access target environments. Ensure a test worker cannot alter approvals or records to convert failures into passes.

## Change impact
Use graph edges from components -> tests -> requirements -> risks and source regulations to propose reruns. Where links are incomplete mark **UNKNOWN IMPACT**, not safe.

---

### Continue exploring

[release status](RELEASE_STATUS.md) · [roadmap](ROADMAP.md) · [All guides](README.md) · [Project homepage](../README.md)
