# HealthQualify — Safety, regulatory and warranty limitations

> **Developer alpha. Synthetic data only. Not a validated regulated-production system.**

HealthQualify is open-source development tooling for healthcare software qualification **demonstrations**, synthetic test execution, requirements-to-test traceability and advisory investigation workflows.

## No regulatory clearance or approval claim

HealthQualify is **not represented as FDA-cleared, FDA-approved, FDA-qualified, or certified**, and has not been established as compliant with FDA 21 CFR Part 11, applicable GxP validation requirements, EU Annex 11, HIPAA, or comparable jurisdiction-specific requirements. No automatic status, PASS result, cryptographic hash, draft finding or reviewer acknowledgment constitutes a regulated qualification approval or electronic signature.

The project is not for diagnosis, treatment, patient monitoring, device actuation or direct clinical decision-making. Do not enter PHI, connect it to live medical devices, or integrate it with production hospital systems without a separately approved, independently assessed deployment and risk-management process.

## AI-specific limitations

Five deterministic advisory investigators run without a language model. Optional local Ollama/Qwen output is **draft and unverified**. AI can make incorrect or unsupported statements. It does not change the underlying deterministic PASS/FAIL status, sign approvals, close deviations or authorize software release. Require appropriately qualified human investigation and independent confirmation of sources.

## User responsibility

The adopting organization is responsible for defining intended use; legal, quality and risk assessment; supplier qualification; test/validation plans; cybersecurity; privacy; records and electronic-signature applicability; change controls; and all applicable third-party licenses. A public-source citation or suggested regulatory mapping is not legal or regulatory advice.

The software is distributed under [Apache License 2.0](LICENSE), including its warranty and liability provisions. This supplemental notice does **not** amend the Apache license or take away permissions it grants. Seek qualified regulatory and legal guidance for regulated deployment.
