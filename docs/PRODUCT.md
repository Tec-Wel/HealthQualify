![Project reference documentation](assets/category-reference.svg)

[← **Documentation home**](README.md) &nbsp; / &nbsp; **Project reference**

# HealthQualify — unified product specification (draft)

> **What you'll learn:** Understand the product mission, planned modules, target users, and explicit non-goals.

**On this page:** [Mission](#mission) · [Target users](#target-users) · [Functional modules](#functional-modules) · [Regulatory scope — context dependent](#regulatory-scope-context-dependent)

---


## Mission
A self-hosted, AI-optional healthcare qualification and computer software assurance platform with one chain of accountability: **regulatory source / intended use → risk → approved requirement → approved protocol → execution → evidence → deviation → human disposition → controlled release**.

## Target users
Healthcare software developers and DevOps, hospital IT, laboratory integration teams, validation/quality engineers, quality approvers and auditors.

## Functional modules
| ID | Module | Definition |
|---|---|---|
| M01 | System registry | System, site, owner, environment, version, intended use, criticality |
| M02 | Regulatory intelligence | Official source retrieval, version history, binding/guidance/draft status, applicability review |
| M03 | Risk and requirements | URS/FRS, risks, sources, reviewer-approved baselines |
| M04 | Protocol Studio | Versioned IQ/OQ/PQ and CSA plans, acceptance criteria, manual and automated cases |
| M05 | Qualification runner | Sandboxed deterministic test adapters, explicit statuses and environment identity |
| M06 | HealthPacks | LIS/HL7 first; FHIR/EHR, device integration, GxP and AI later |
| M07 | EvidenceChain | Raw test results, protocol hash, runner version, provenance, hashes and verifiable export |
| M08 | Traceability graph | Regulation/risk/requirement/test/run/result/evidence/change links |
| M09 | DeviationFlow | Finding, severity, owner, investigation, CAPA, retest and disposition |
| M10 | Review and approval | Controlled changes, reviewer identity and auditable human decisions |
| M11 | Continuous Qualification | Release-triggered impact review, reruns, unknown-impact escalation |
| M12 | ModelQual & optional copilot | Model/prompt/dataset versioning, safety metrics; locally hosted or approved external AI |

## Regulatory scope — context dependent
- US 21 CFR Part 11 where relevant to electronic records/signatures.
- EU GMP Annex 11 and Annex 15 where applicable to GMP systems.
- GAMP 5 as guidance (licensed proprietary material must not be copied into the repo).
- FDA Computer Software Assurance guidance for its *specific* production/QMS software scope.
- ISO 13485 and IEC 62304 where applicable to medical devices/software.
- HL7 FHIR, HL7 v2, DICOM as technical interoperability specifications rather than universal laws.
- Proposed requirements are never marked effective solely from a publication alert.

## Required workflows
1. Register system and intended use; select scope after risk/applicability review.
2. Import or draft requirements with source references; obtain human baseline approval.
3. Link every protocol case to requirement, test implementation and defined acceptance criteria.
4. Execute approved tests in an authorized test environment; separately record manual witnessed tests.
5. Capture raw results and evidence files; generate hashes and a manifest. Preserve statuses PASS / FAIL / ERROR / NOT_RUN.
6. Create deviations for failures and evidence gaps; require investigation and linked retest.
7. Obtain appropriate review/approval; never make a regulatory certification claim.
8. On software or regulatory changes, propose affected tests and demand human review for unknown impact.

## Optional AI agents
Regulatory Advisor, Risk/GAMP Advisor, Requirements Author, IQ Specialist, OQ Specialist, PQ Specialist, Deviation Investigator. They produce **drafts and suggestions only**. They cannot modify approved baselines, produce execution evidence, close deviations or approve qualification.

## First reference system
Synthetic LIS integration. Seed cases include patient/sample mismatch, incorrect unit conversion, missing critical result notification, cross-tenant access and missing audit record. Run with no PHI, no network services, no AI API.

## Non-goals for first release
- Medical equipment physical calibration or hospital production connections.
- Formal Part 11 electronic-signature system.
- Automatic regulatory applicability/legal determinations.
- LLM judging whether a clinical or regulatory requirement passed.
- Claims of being FDA-approved, GxP-certified, or universally validated.

## Competitive advantage to validate
Against equivalent standalone scripts, requirements coverage tooling, and standard pytest + GitHub Actions workflows:
measure setup time, seeded failure detection, false results, evidence verifiability, repeatability, maintenance burden, and correct requalification impact. No performance superiority claims until benchmarks are run.

---

### Continue exploring

[release status](RELEASE_STATUS.md) · [roadmap](ROADMAP.md) · [All guides](README.md) · [Project homepage](../README.md)
