![Start here documentation](assets/category-start.svg)

[← **Documentation home**](README.md) &nbsp; / &nbsp; **Start here**

# Frequently asked questions

> **What you'll learn:** Find concise explanations of common setup, evidence, security, and adoption questions.

---


### What is HealthQualify?
An open-source developer-alpha set of deterministic synthetic qualification tools, traceability/evidence utilities, local SQLite workflow and conservative change-impact review.

### Can I run it on Windows, macOS or Linux?
Yes, with Python 3.10+ (3.12 recommended) and Git. See [Installation](INSTALLATION.md) for OS-specific commands.

### Does it need AI, a cloud account or hospital connection?
No for the core synthetic runner. Optional local AI drafts and restricted staging adapters are separate opt-in capabilities. AI cannot approve qualification.

### Why does my first run exit with code 1?
The bundled LIS example intentionally has **five failing and two passing cases**. This demonstrates defect detection. Check `results.json`.

### How do I know the run worked?
Run the unit suite, inspect expected assertions, save the manifest digest separately and run `v05cli verify`. See [Evaluation](EVALUATION_GUIDE.md).

### Can I give it my own GitHub repository and get automatic qualification?
No. You must author supported synthetic fixtures and map requirements/tests; automatic test discovery and general repository introspection are not present.

### Is v0.3 JSON the same as the SQLite workspace protocol?
No. Standalone `v05cli` uses strict v0.3 JSON. `appcli protocol-add` stores v0.2 JSON; no automatic bridge exists.

### Can it connect to live FHIR, HL7, DICOM or devices?
Only restricted non-production test capabilities exist. FHIR HTTPS GET requires explicit approved origin, read-only access and authorization. HL7 frame, DICOM metadata and device snapshot tools are offline/synthetic. Production connections are not supported.

### Can I use PHI, patient records or clinical data?
**No.** This alpha is intended only for synthetic/public non-sensitive data. Do not use production healthcare records.

### Does PASS mean FDA compliant or GxP validated?
**No.** PASS means only a specific synthetic assertion passed. Regulatory suitability and organizational approvals require independent qualified processes.

### Can the QA reviewer digitally sign a protocol?
Local review/attestation receipts are technical events, **not qualified Part 11 electronic signatures**.

### What happens if a changed file has no test mapping?
HealthQualify reports `UNKNOWN_IMPACT`, recommends all existing tests and requires human review.

### Can it close deviations automatically?
No. Technical review, CAPA and evidence-linked retesting are distinct; an operator's disposition is not a formal QMS approval.

### Can I deploy with Docker?
Compose initializes a local SQLite workspace and deliberately exposes no HTTP port. Cloud deployment must be engineered and assessed independently.

### Is there an API?
A **loopback-only** authenticated alpha API defaults to port 8877. See [API reference](API_REFERENCE.md). Do not expose it to the public internet.

### Is it licensed for open-source use?
The repository uses Apache-2.0 for original code. Check any third-party dependency and standards-content licenses.

### Where do I report a problem?
Use GitHub Issues with a sanitized reproducer, or [Security policy](../SECURITY.md) for private security reporting. Never submit PHI or secrets.

### What should I read first?
[Getting started](GETTING_STARTED.md) → [Evaluation](EVALUATION_GUIDE.md) → [Your own project](USER_GUIDE.md) → [Verification](VERIFICATION_GUIDE.md).

---

### Continue exploring

[getting started](GETTING_STARTED.md) · [end to end workflow](END_TO_END_WORKFLOW.md) · [All guides](README.md) · [Project homepage](../README.md)
