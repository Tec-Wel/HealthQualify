# Privacy and local data handling — developer alpha

**Scope:** HealthQualify Local Edition and its local Python tooling. This notice describes application behavior, not GitHub's or an operating system's independent data practices. HealthQualify is for **synthetic or public nonsensitive development data only**. **Do not enter PHI, patient records, credentials for clinical systems, or confidential employer information.**

## Data stored locally

The default Local Edition creates `~/.healthqualify/local-edition.db` (SQLite), which can include local usernames, salted password verifiers, account roles, authentication sessions, systems, draft protocols, synthetic test results, findings, agent observation records, QA review decisions, and audit metadata. Other CLI commands may create SQLite databases and evidence/report directories at user-selected paths. Files may remain after you close the application.

The application does **not** require your name, email address, cloud account, purchased model token, or an internet connection to perform core qualification exercises. An administrator chooses local usernames; **avoid real identifiers**. Protect your workstation and its backups: local storage is not a protected enterprise multi-tenant or WORM environment.

## Network and optional AI

The Local Edition HTTP dashboard binds to loopback (`127.0.0.1`) by default. Core synthetic qualification and deterministic agent workflows do not require a hosted AI provider. **Local Qwen is disabled by default**. If the operator enables it and actively requests a model explanation, the application contacts the local Ollama endpoint `http://127.0.0.1:11434` and sends bounded, prepared investigation context. This does not automatically mean that a separately installed Ollama service, OS or model has no other network activity: assess and configure those components independently.

Additional explicitly enabled adapters and integrations in this repository can make network calls to approved origins. Fetching model weights, installing dependencies, visiting hosted documentation, downloading releases, using GitHub Issues, or opening externally hosted shields/badges involves third parties and their own privacy terms.

## Telemetry and sharing

The core Local Edition does not contain a mandatory hosted telemetry account or an application analytics upload requirement. This statement is **not** a third-party privacy guarantee and does not describe the optional external services above. This developer alpha has not completed an independent traffic audit. Do not rely on it for sensitive information.

## Security, data deletion and retention

The local administrator controls access to the local installation. Browser sessions are temporary; SQLite application data and exported evidence persist until you intentionally delete them. To remove the default Local Edition workspace, **close the app**, preserve any reports you need, then delete `~/.healthqualify/local-edition.db` and any local copies/backups you created. Review other locations provided using `--db` and report output flags. Do not assume deleting the database securely erases file-system snapshots, cloud-sync copies, backups, or Git history.

The software does not currently offer a verified organization-managed retention schedule, HIPAA/DPDP compliance package, data subject request service, or protected production record repository. Never use it with PHI.

## Changes and inquiries

Changes in model integrations, analytics, network behavior or cloud hosting require updating this notice before release. See [SECURITY.md](SECURITY.md) for private vulnerability reporting and [SUPPORT.md](SUPPORT.md) for non-security project support. Maintainers should approve any named controller/contact details before publication.

**Last updated:** 2026-11-17
