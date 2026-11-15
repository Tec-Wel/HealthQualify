![Project reference documentation](assets/category-reference.svg)

[← **Documentation home**](README.md) &nbsp; / &nbsp; **Project reference**

# Roadmap and acceptance gates

> **What you'll learn:** Review historical phases and proposed future functionality without interpreting plans as shipped features.

**On this page:** [v0.1 Foundation — deterministic reproducibility](#v01-foundation-deterministic-reproducibility) · [v0.2 Qualification workspace](#v02-qualification-workspace) · [v0.3 Continuous qualification](#v03-continuous-qualification) · [v0.4 Healthcare AI and intelligence](#v04-healthcare-ai-and-intelligence)

---


## v0.1 Foundation — deterministic reproducibility
- Working CLI with allowlisted checks, JSON schema validation, explicit failure exit codes.
- IQ/OQ/PQ test cases linked to requirements and run outcomes.
- Synthetic laboratory fixture with intentionally failing cases.
- Evidence export: protocol bytes, results, hashes, manifest, integrity verification.
- Unit tests and GitHub Actions.

**Gate:** Runs offline without an AI API; independently detects intentional failures; never converts ERROR or NOT_RUN into PASS. No production/PHI usage.

## v0.2 Qualification workspace
- System registry, URS/FRS import, risk and applicability review.
- Protocol versions and controlled human approval workflow.
- Deviation management with retesting and reviewer disposition.
- Regulatory source library and clearly labeled legal status.
- CSA path in addition to IQ/OQ/PQ.
- JSON/HTML/PDF, Word/Excel reports from **recorded evidence**.

## v0.3 Continuous qualification
- GitHub/GitLab CI links and release baselines.
- Conservative change-impact graph and incomplete-link escalation.
- FHIR/HL7 adapters with synthetic testing.
- Cloud-neutral Docker deployment; web dashboard.
- Enhanced artifact signatures, audit trail and data governance.

## v0.4 Healthcare AI and intelligence
- ModelQual datasets/metrics, versioned AI evaluation and regression tests.
- Optional local/hosted AI for protocol drafts, source-linked regulatory advice and deviation explanations.
- Approval gates remain non-AI.
- Optional daily regulatory change ingestion with human applicability review.

## v1.x enterprise readiness
- Tested installation, backup and recovery, restricted workers, RBAC, identity and audit controls.
- QMS integrations, qualified electronic signatures when applicable, retention.
- Validation/assurance of HealthQualify itself for regulated use.

## Measurement
Compare the same synthetic LIS requirements and seeded defects with standalone scripting, traceability tooling and baseline pytest. Track setup time, coverage of seeded defects, false positives, reproducibility, artifact integrity, maintenance and affected-test impact accuracy.

All milestones are planned, not completed product claims.

---

### Continue exploring

[release status](RELEASE_STATUS.md) · [product](PRODUCT.md) · [All guides](README.md) · [Project homepage](../README.md)
