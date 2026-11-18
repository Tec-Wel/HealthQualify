# Governance and maintainership

HealthQualify is an early-stage community-facing project maintained through its GitHub repository. This page describes technical project decisions; it **does not establish legal ownership** or license any third-party IP.

## Decisions

- Issues propose features, design changes, and safety concerns.
- Focused pull requests carry tests, documentation and a safety impact statement.
- Repository maintainers review compatibility, source provenance, licensing, threat boundaries, and test results before merging.
- Medical, regulatory or legal claims require an appropriately qualified independent reviewer.
- Deterministic checks and human quality authority take precedence over generative suggestions.

## Trademark and owner authorization

HealthQualify software is governed by [Apache-2.0](LICENSE). The [trademark guidance](TRADEMARK_POLICY.md) covers accurate origin references and misleading unofficial branding, without reducing rights under the software license. Legal owner, patent position and authority to release remain unverified; see the [owner/IP decision checklist](docs/OWNER_IP_RELEASE_DECISION.md). Do not treat repository administrative access as proof of copyright ownership.

## Release authority

Only repository maintainers authorized by the repository owner may tag releases or publish distributions. Changing the repository from private to public is a **separate explicitly approved launch decision** after documented owner/IP, history/secrets, security and third-party-license gates pass. A passing CI run alone does not authorize publication.

## Contributions and intellectual property

Contributors must have rights to share their work under the project's Apache-2.0 terms. Do not import employer-owned, hospital-owned, patient or paywalled standards content without explicit permission. We request a developer certificate of origin (DCO) sign-off on future code contributions; see [CONTRIBUTING.md](CONTRIBUTING.md).

## Conflict resolution

Maintainers should explain accepted/rejected changes in GitHub issues or pull requests and identify competing interests when they materially affect project policy. A named governance steering group is not asserted at this stage. [SUPPORT.md](SUPPORT.md) explains support boundaries.
