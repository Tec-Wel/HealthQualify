# Regulatory and standards mapping — applicability, not a compliance claim

**Warning:** HealthQualify does not automatically establish applicability, regulatory approval, FDA certification, e-signature validity or conformity to these frameworks. This is a learning/index document; verify the current official text, jurisdiction, product classification and institutional SOPs before use.

## Framework map

| Framework / specification | Typical relevance | Documentation/test artifacts to consider | Current HealthQualify support |
| --- | --- | --- | --- |
| FDA Computer Software Assurance (CSA) guidance | Specified medical-device production/QMS software scope | Intended use, risk-based assurance strategy, evidence | Draft-only CSA profiles and tests; no regulated approval |
| US 21 CFR Part 11 | Where regulated electronic records/signatures rules apply | Identity, audit, record integrity, signature meaning, retention | Technical receipts/reviewer events; **not compliant e-signatures** |
| EU GMP Annex 11 | Computerised systems in applicable GMP context | Risk, supplier assessment, system validation, access/backup/audit | Sample artifacts; no validated GMP deployment |
| EU GMP Annex 15 | Qualification/validation in applicable GMP context | Qualification plan, protocols, deviations, approvals | Synthetic IQ/OQ/PQ methodology; no formal qualification |
| GAMP 5 | Industry guidance, licensed content | Risk-scaled lifecycle, good engineering practices | Conceptual references only; do not reproduce licensed text |
| ISO 13485 | Medical-device QMS where applicable | Design controls, traceability, records, change control | Draft traceability concept, not QMS certification |
| IEC 62304 | Medical device software lifecycle where applicable | Safety classification, requirements/test traceability, maintenance | Engineering building blocks, not conformant lifecycle suite |
| HL7 v2 / FHIR | Healthcare interface standards, not universal laws | Versioned message/profile assertions | Synthetic HL7 fields, restricted FHIR field assertion |
| DICOM | Medical imaging interoperability | Metadata/transfer/profile validation | Synthetic offline metadata only |

## Evidence-to-obligation analysis worksheet

For each legal or standard clause *owned and verified by your organization*, populate:

| Field | Question |
| --- | --- |
| Source ID and revision | What exact official/authorized document is applicable? |
| Applicability and rationale | Why does this clause apply to this system? |
| Organization control | What SOP, policy or design control implements it? |
| Requirement and risk IDs | How is it translated into a testable control? |
| Test or manual verification | What execution and evidence are required? |
| Responsible reviewer | Who is authorized to assess adequacy? |
| Gap and disposition | What remains unsupported by tooling or the system? |

The synthetic `source_references` registry checks only that each `source_id` exists, **not** that its entry is authoritative, current or legally applicable.

## Official starting points

- FDA guidance and software assurance: [FDA guidance documents](https://www.fda.gov/regulatory-information/search-fda-guidance-documents)
- US regulations: [eCFR 21 CFR Part 11](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-A/part-11)
- EU GMP guidance: [EudraLex Volume 4](https://health.ec.europa.eu/medicinal-products/eudralex/eudralex-volume-4_en)
- ISO standards catalog: [ISO](https://www.iso.org/standards.html)
- IEC publications: [IEC](https://webstore.iec.ch/)
- [HL7 FHIR](https://hl7.org/fhir/) · [DICOM](https://www.dicomstandard.org/)

These references are navigation aids only. Some standards are copyrighted/licensed, and a tool-generated draft must not be represented as a definitive legal determination.

See [Security & limitations](SECURITY_AND_LIMITATIONS.md), [Qualification](QUALIFICATION_METHODOLOGY.md).
