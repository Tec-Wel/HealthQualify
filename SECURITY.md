# Security policy

## Supported scope and versions

HealthQualify is a **developer-alpha** open-source project. Current code is suitable only for synthetic/public non-sensitive evaluation and is **not** a production clinical, PHI, regulated records, device-control or qualification approval platform. There is no announced long-term security-support policy or SLA. Please assess the latest commit and release notes before testing.

## Confidential reporting capability

The repository owner must enable any available GitHub private vulnerability reporting feature in repository Settings and verify it with a test account, **if supported for the repository's visibility**. An optional intake form is stored at [`.github/VULNERABILITY_REPORT.yml`](.github/VULNERABILITY_REPORT.yml); a form file does not enable reporting. Until a working confidential reporting route is confirmed, **do not claim that researchers can submit vulnerability reports privately**. Maintainers must provide an approved private channel; do not invent an email address. See [release evidence package](docs/RELEASE_EVIDENCE_PACKAGE.md).

## Report vulnerabilities responsibly

**Do not post exploitation details, credentials, sensitive integrations, real patient data or attack artifacts in a public issue.** Use GitHub's **Report a vulnerability** private advisory mechanism **if enabled** for this repository:

1. Open the repository's **Security** tab on GitHub.
2. Select **Report a vulnerability** if the maintainers have enabled private vulnerability reporting.
3. Supply a minimal **synthetic-only** reproducer, affected commit, impact, conditions, expected behavior and safe remediation recommendation.
4. If private reporting is unavailable, contact the repository maintainers through a private channel before sharing exploit details. No dedicated security email address is currently represented here.

Please do not attempt to access third-party healthcare systems, accounts or data. Avoid running tests against production endpoints.

## Useful reporting information

- Full Git commit SHA and Python version
- Affected command/module/function and configuration
- Severity rationale and attack prerequisites
- Sanitized reproduction steps with test-only data
- Expected behavior and actual observed output
- Whether disclosure is coordinated with another library/vendor

## Maintainer response

The maintainer should acknowledge, triage, reproduce without PHI, scope affected versions, fix with regression tests, review related trust boundaries and coordinate disclosure. **No specific response time is promised.**

## Security capabilities and gaps

See [Security model](docs/SECURITY_MODEL.md), [Security and limitations](docs/SECURITY_AND_LIMITATIONS.md), and [Production readiness](docs/PRODUCTION_READINESS_CHECKLIST.md). Hashes and cryptographic technical receipts are **not** legal electronic signatures or evidence immutability.
