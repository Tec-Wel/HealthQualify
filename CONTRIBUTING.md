# Contributing

**New to this repository?** [Follow the visual first-contribution guide](docs/CONTRIBUTOR_VISUAL_GUIDE.md) or [review the reusable design system](docs/DESIGN_GUIDELINES.md) before proposing README, docs, or dashboard styling changes. to HealthQualify

Thank you for helping build transparent, reproducible open-source healthcare software assurance tooling.

## Before contributing

Read [README](README.md), [Getting started](docs/GETTING_STARTED.md), [Architecture](docs/ARCHITECTURE.md), [Security & limitations](docs/SECURITY_AND_LIMITATIONS.md), and current [issues](https://github.com/Tec-Wel/HealthQualify/issues). The repo is a **developer alpha**; do not claim regulatory validation or add real patient data.

## Development setup

```bash
git clone https://github.com/Tec-Wel/HealthQualify.git
cd HealthQualify
python -m unittest discover -s tests -v
```

Use Python 3.12 where possible. Optional security/DICOM tests may need:

```bash
python -m pip install -r requirements-security.txt
```

For Windows PowerShell and virtual environments, see [Installation](docs/INSTALLATION.md).

## Make a focused pull request

1. Create a branch from current `main`; use a descriptive name.
2. Link the issue, describe current behavior, expected behavior, safety boundaries and changed files.
3. Add unit tests for normal, failure, malformed input and tampering cases as relevant.
4. Update user-facing documentation and examples whenever commands, schema or behavior change.
5. Run `python -m unittest discover -s tests -v` and relevant synthetic examples.
6. Preserve expected nonzero exits from seeded-failure protocols.
7. Open a PR; wait for CI; resolve comments before merge.

## Architecture rules

- Core synthetic assertions must be deterministic, bounded and network-disabled by default.
- Do not let AI create authoritative verdicts or approval events.
- Reject unknown protocol fields and unsafe paths; preserve explicit FAIL/ERROR/NOT_RUN.
- Do not silently mark missing requirement coverage as passing.
- Avoid overwriting evidence or trusted digests; use new directories.
- Ensure `UNKNOWN_IMPACT` never silently becomes an approval.
- Preserve the distinction between the standalone strict v0.3 runner and SQLite v0.2 workspace.
- Do not copy copyrighted standards or third-party source without license review.

## Documentation quality checklist

Commands must be real, copyable, scoped to the repository root and clear about OS differences, dependencies, expected output and exit code. Placeholder URLs should be labelled. Claims about security, compliance and integrations must match actual code and tests. New docs should link from the README and should not imply new features are production-ready.

## Reporting issues

Provide OS, Python version, Git commit, command, expected/actual behavior, and sanitized reproducer. Never include PHI, API tokens, passwords, real clinical fixtures or confidential hospital connection details. Report possible vulnerabilities privately.

## Licensing

By contributing, follow the repository [Apache-2.0 license](LICENSE) and applicable attribution obligations.
