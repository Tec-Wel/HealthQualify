![Trust & operations documentation](assets/category-trust.svg)

[← **Documentation home**](README.md) &nbsp; / &nbsp; **Trust & operations**

# Security, privacy, assurance and product limitations

> **What you'll learn:** Learn the privacy, compliance, storage and evidence limitations that apply to the developer alpha.

**On this page:** [Classification](#classification) · [Allowed development practices](#allowed-development-practices) · [Security controls implemented versus missing](#security-controls-implemented-versus-missing) · [Regulatory terms: use accurately](#regulatory-terms-use-accurately)

---


## Classification

**HealthQualify is a developer alpha.** It is not qualified for regulated production use, patient care, medical device control, protected health information (PHI), customer qualification approval, or automatic FDA/GxP certification. No successful test run, manifest verification or local review receipt changes that status.

## Allowed development practices

- Use **synthetic or public non-sensitive** test data only.
- Keep a dedicated local or explicitly authorized isolated non-production test environment.
- Store API credentials and encryption/signing material outside Git and outside exported evidence.
- Use exact approved HTTPS staging origins for any opt-in FHIR checks.
- Keep user-supplied artifacts bounded and sanitize logs, issue reports and examples.
- Preserve recorded evidence and independent digests; do not rewrite old results after a defect.
- Require qualified human review under the organization's own QMS where applicable.

## Security controls implemented versus missing

| Area | Present | Not established by this repository |
| --- | --- | --- |
| Core execution | Offline allowlisted synthetic tests; network/AI/destructive disabled | Isolation for arbitrary third-party code or production workflows |
| API | Loopback binding, PBKDF2-backed local identity, scoped roles and short-lived session tokens | Public TLS infrastructure, MFA/SSO, mature threat detection, multi-tenant authorization |
| Evidence | SHA-256, independent manifest digest, deterministic replay; optional encrypted/signed technical export | Tamper-proof audit storage, external trusted timestamp, HSM/KMS lifecycle, regulated e-signatures |
| Privacy | Synthetic fixture policy, bounded test operations | HIPAA/DPDP compliance, DPA/BAA, PHI handling or clinical data retention |
| Interoperability | Restricted FHIR read, offline HL7/DICOM/device probes | Complete clinical integration profiles or production network qualification |
| Backup | SQLite consistent backup, integrity verification, verified restore to a new path | Encrypted offsite storage, tested operational disaster recovery, managed retention |
| Human decisions | Demo reviewer separation and technical QA attestations | Validated legal signatures, institutional SOPs and regulator-specific compliance |

## Regulatory terms: use accurately

- **IQ/OQ/PQ** denote qualification activities **where justified** by the intended use and risk.
- **CSA** refers to risk-based computer software assurance in its applicable regulatory context; not every hospital application must follow the same pathway.
- **21 CFR Part 11**, **EU GMP Annex 11/15**, **ISO 13485**, **IEC 62304**, **FHIR**, **HL7**, and **DICOM** have different applicability and purposes. Listing them is not a statement that HealthQualify complies with all of them.
- **Technical Ed25519 receipt** or HMAC seal is not equivalent to a legally valid regulated electronic signature.
- **PASS** means an executed synthetic assertion passed. It is not proof of complete safety, security, conformance or regulatory approval.
- Optional AI can produce draft suggestions but must not issue authoritative test PASS/FAIL or approval decisions.

## Risks users must assess before any expanded use

Authorization, source validation, threat modeling, egress control, audit tamper resistance, time synchronization, identity governance, QMS integration, tool validation, dependency security, backup/recovery, retention and independent regulatory review. Production use remains gated until the organization's formal process establishes suitability and the software gains necessary hardening.

## Reporting vulnerabilities

Do not disclose exploitable secrets, credentials, internal systems or PHI in public issues. Use the repository's available private reporting mechanism if configured, or contact the maintainers through an appropriate private channel. No public contact address is assumed here.

See [Release status](RELEASE_STATUS.md), [Security and interoperability alpha](SECURITY_INTEROP_V04.md), and [Verification](VERIFICATION_GUIDE.md).

---

### Continue exploring

[security model](SECURITY_MODEL.md) · [verification guide](VERIFICATION_GUIDE.md) · [All guides](README.md) · [Project homepage](../README.md)
