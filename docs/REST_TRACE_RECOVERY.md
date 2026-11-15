# Issue hardening: REST, traceability, and backup restore

This is a synthetic-data developer implementation, not a clinical or regulated-production release.

## Issue #2 — Local read-only REST checks

`healthqualify/rest_local.py` provides a JSON assertion against an explicitly authorized **127.0.0.1** `/test/` endpoint. It enforces:

- GET only, no redirect, no query strings, no userinfo
- Bounded timeout (1–8 seconds), bounded response size (up to 256 KiB)
- No PHI/observed/expected response values persisted in the returned assertion
- PASS/FAIL and metadata only; no certification claims

```bash
python -m healthqualify.v05cli rest-check-local \
  http://127.0.0.1:9999/test/synthetic status '"ok"' --authorize-synthetic
```

A separate local test fixture server must be running. The regression tests mock HTTP and never call a production network. Existing synthetic HL7/FHIR and staging FHIR adapters remain unchanged. Full production HL7/FHIR/DICOM site integration is still pending.

## Issue #4 — Evidence links

Every stored execution now attaches a stable `hq-run:<uuid>/test/<test-id>` internal identifier to each test result. Requirement traceability rows list corresponding evidence refs. A run additionally binds `protocol_id` and `protocol_digest`, while observation values stay redacted.

These identifiers are internal references, not externally trusted artifact signatures or permanent retention guarantees.

## Issue #8 — Safe SQLite recovery

```bash
python -m healthqualify.v05cli backup source.db backup.db
python -m healthqualify.v05cli backup-verify backup.db --trusted-sha256 <saved-digest>
python -m healthqualify.v05cli backup-restore backup.db restored.db --trusted-sha256 <saved-digest>
```

Restore demands a separately trusted checksum, validates the SQLite database, and refuses to overwrite a destination. Backups are **not encrypted**, and this is not a production disaster recovery exercise. Use only synthetic data.

## Release constraints

These improvements advance issues #2, #4 and #8 but do not satisfy their entire acceptance criteria. Independent privacy, security, hospital integration, protected evidence and regulated record validation remain required.
