![Trust & operations documentation](assets/category-trust.svg)

[← **Documentation home**](README.md) &nbsp; / &nbsp; **Trust & operations**

# Production readiness and regulated-use gating checklist

> **What you'll learn:** Identify security, operational, regulatory and QMS controls that remain unmet for production use.

**On this page:** [Evaluation status](#evaluation-status) · [Evidence collection worksheet for each gate](#evidence-collection-worksheet-for-each-gate) · [Pilot decision framework](#pilot-decision-framework) · [Signoff boundaries](#signoff-boundaries)

---


**Default disposition: NO-GO for production, PHI, regulated electronic records, patient care or device control.** This template allows a prospective adopter to assess gaps; checking boxes does not automatically authorize use.

## Evaluation status

| Area | Alpha observation | Required independent gate | Current state |
| --- | --- | --- | --- |
| Intended use | Synthetic engineering demos | Customer-approved intended use and risk classification | OPEN |
| QMS integration | Offline JSON handoff | Approved SOPs, vendor integration reconciliation, independent human approval | OPEN |
| Electronic records/signatures | Technical hashes and attestations | Part 11/Annex 11 applicability, validated controls, identity/signature/time/retention | OPEN |
| Data privacy | Synthetic only | PHI protection, HIPAA/DPDP analysis where applicable, DPA/BAA, data governance | OPEN |
| Identity | Local roles/passwords | Organization SSO/MFA, lifecycle, least privilege, periodic review | OPEN |
| Network/API | Loopback HTTP | TLS, private ingress/egress, DNS controls, rate limiting, API security tests | OPEN |
| Multi-tenancy | No operational tenant isolation | Threat-tested tenant boundaries and access enforcement | OPEN |
| Storage | SQLite/local filesystem | Managed encrypted DB/object store, backups and WORM where required | OPEN |
| Evidence trust | SHA-256 + replay | Trusted time, independent custody, signed/versioned verifier, retention validation | OPEN |
| Clinical interoperability | Restrained synthetic checks | Approved/staged vendor profiles, integration qualification and clinical risk assessment | OPEN |
| Operations | Local runbook | Monitoring, alerting, incident response, DR/restore exercises, change control | OPEN |
| Release governance | Advisory impact/reviewer record | Protected branches/tags, release authority and signed-off validation evidence | OPEN |
| Security assurance | Automated repository tests | Threat model, independent penetration test, supply-chain scanning, patch plan | OPEN |
| Tool validation | Developer test suite | Validation of HealthQualify itself for its actual regulated intended use | OPEN |

## Evidence collection worksheet for each gate

For **every** gate, capture: control owner, policy/acceptance criterion, evidence link/digest, date/source revision, reviewer, independent test result, exceptions, remediation and approved decision under an external controlled process.

```text
Gate:
Owner:
Applicable policy/source and revision:
Test/verification plan:
Observed technical evidence:
Independent trusted digest/location:
Open risks/deviations:
Review authority and disposition:
Status: OPEN / BLOCKED / REVIEWED OUTSIDE TOOL
```

The text `REVIEWED OUTSIDE TOOL` is not an implementation of certification; authority and legal suitability must be determined by the organization.

## Pilot decision framework

**Allowed:** non-production synthetic demonstration, benchmark and secure architectural evaluation. **Blocked:** patient data, hospital production integrations, electronic-signature reliance, compliance claims, or automated clinical/regulated release decisions.

## Signoff boundaries

Even if every future readiness row receives evidence, legal and operational sign-off must occur through the organization's own validated QMS and approval structure. HealthQualify's `qualification_approved` field remains false in its current synthetic protocols.

See [Deployment](DEPLOYMENT_GUIDE.md), [Security model](SECURITY_MODEL.md), [Regulatory mapping](REGULATORY_MAPPING.md), [Feature matrix](FEATURE_MATRIX.md).

---

### Continue exploring

[security model](SECURITY_MODEL.md) · [verification guide](VERIFICATION_GUIDE.md) · [All guides](README.md) · [Project homepage](../README.md)
