![Trust & operations documentation](assets/category-trust.svg)

[← **Documentation home**](README.md) &nbsp; / &nbsp; **Trust & operations**

# Operations runbook — local developer-alpha environment

> **What you'll learn:** Follow safe local startup, health checks, backup, restore, and incident-handling steps.

**On this page:** [1. Before opening the service](#1-before-opening-the-service) · [2. Initialize, bootstrap and start](#2-initialize-bootstrap-and-start) · [3. Daily developer checks](#3-daily-developer-checks) · [4. Backup and verify](#4-backup-and-verify)

---


**Purpose:** reproducible startup, health diagnosis, backup, recovery and incident triage for a non-production synthetic environment. **Not** an approved production SOP, service-level commitment or disaster recovery plan.

## 1. Before opening the service

Record Git SHA, Python version, host owner, non-production environment, test-only data policy and location of the SQLite DB. Make sure the host is under your control and no external network exposure is configured.

```bash
git rev-parse HEAD
python --version
python -m unittest discover -s tests -v
```

## 2. Initialize, bootstrap and start

```bash
python -m healthqualify.appcli --db demo.db init
python -m healthqualify.appcli --db demo.db bootstrap-admin admin_owner
python -m healthqualify.appcli --db demo.db serve
```

Bootstrap only once per new identity database. The CLI prompts for credentials. Open `http://127.0.0.1:8877/health` from the same machine, not from a remote system. The expected JSON includes `"regulated": false`.

## 3. Daily developer checks

| Check | Command / inspection | Expected | Response to failure |
| --- | --- | --- | --- |
| Code regression | `python -m unittest discover -s tests -v` | Tests pass | Stop demo rollout; inspect failing test |
| Local API health | GET `127.0.0.1:8877/health` | 200 and secure-alpha | Verify process/port; do not bind externally |
| Identity/session | Login with dedicated local test account | Short-lived bearer token | Check roles and expiration, not bypass |
| Synthetic fixture test | `v05cli run ... --out NEW_DIR` | 2 PASS / 5 FAIL on bundled LIS | Compare expected fixture and checkout |
| Evidence verification | `v05cli verify ... --trusted-manifest-sha256 DIGEST` | True for original | Preserve files and investigate mismatch |
| Release impact | `quality_cli release-plan` or CI advisory | Human review required | Escalate unknown mapping |

## 4. Backup and verify

For **synthetic SQLite DB only**, with a **new destination**:

```bash
python -m healthqualify.v05cli backup demo.db demo-backup.db
```

Save the returned `sha256` **independently**. Verify:

```bash
python -m healthqualify.v05cli backup-verify demo-backup.db --trusted-sha256 SAVED_DIGEST
```

Restore only into a **new path**, never overwrite the original:

```bash
python -m healthqualify.v05cli backup-restore demo-backup.db demo-restored.db --trusted-sha256 SAVED_DIGEST
```

These files are **not encrypted by the backup tool** and the commands are not operational disaster recovery validation. Secure or delete test-only copies under your organization's rules.

## 5. Technical evidence retention and hold

```bash
python -m healthqualify.quality_cli retain example-package.json qms_handoff --folder .healthqualify/local-vault --days 365 --legal-hold
python -m healthqualify.quality_cli retention-verify RECORD_UUID --folder .healthqualify/local-vault
```

The `--legal-hold` flag and retention date are **metadata** in a local SQLite registry, not OS-enforced WORM protection or legally sufficient evidence retention. Protect and back up the store independently.

## 6. Incident response playbook

**Suspicious evidence mismatch:** stop new run claims; preserve original files, original separately trusted digest, source commit and audit notes. Do not “repair” evidence by overwriting results or simply rehashing the tampered bundle.

**Authentication or credential exposure:** stop loopback service, invalidate sessions if needed, rotate affected local test credentials/secrets, inspect security events and determine whether data left the authorized environment. Never paste secrets in issues.

**Unexpected outbound network request:** halt execution, document destination and authorization, verify code path, isolate workstation if warranted. Strict v0.3 synthetic engine should not require network.

**API unavailable:** check service started, port 8877 and local-only address. Do not “fix” by binding to a public interface.

**Failed recovery:** preserve backup and trusted digest, do not overwrite source DB, repeat in isolated test path and record result.

## 7. Closeout / handover

Collect source commit, interpreter, test outcome, evidence location and trusted digest, unresolved deviations, backup/restore checks, reviewer acknowledgement and known limitations. Do not use a developer-alpha record as formal customer qualification approval.

See [Security model](SECURITY_MODEL.md), [Troubleshooting](TROUBLESHOOTING.md), [Production readiness](PRODUCTION_READINESS_CHECKLIST.md).

---

### Continue exploring

[security model](SECURITY_MODEL.md) · [verification guide](VERIFICATION_GUIDE.md) · [All guides](README.md) · [Project homepage](../README.md)
