# Versioning, documentation and release policy

## Current maturity

HealthQualify uses **developer-alpha** version labels to organize feature development. **v0.3 protocol schema** is distinct from **v0.3 product milestone**, and a `runner_version` string is metadata, not proof of software qualification.

## Working rules

- Git commit SHA is the exact engineering revision for CI/test evidence.
- A GitHub tag/release is a distribution marker; the release-impact workflow produces an **advisory**, never an approval.
- Protocol schema changes require documented compatibility behavior, tests and migration guidance.
- Breaking CLI changes require updated `--help`, reference docs, examples and regression tests.
- Existing evidence must remain bound to the original source protocol bytes and runner; never rewrite old artifacts to match a newer schema.
- Documentation should say **implemented alpha**, **experimental**, **planned** or **unsupported** rather than imply enterprise/compliance readiness.

## Suggested future release checklist (not an implemented automated gate)

1. Freeze and review source changes, issues and dependency advisories.
2. Run unit/security tests plus deterministic synthetic example and integrity verification.
3. Record SHA-bound impact advisory and human review disposition.
4. Review test coverage, failure handling, release notes and migration compatibility.
5. Publish changelog and tag under protected permissions.
6. Verify release artifacts against independently controlled digests.
7. Require external QMS sign-off where applicable; the alpha supplies none.

See [Release status](RELEASE_STATUS.md), [Production readiness](PRODUCTION_READINESS_CHECKLIST.md), and [Testing & CI](TESTING_AND_CI.md).
