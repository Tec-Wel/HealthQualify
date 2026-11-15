![Project reference documentation](assets/category-reference.svg)

[← **Documentation home**](README.md) &nbsp; / &nbsp; **Project reference**

# HealthQualify v0.6 — Quality review, release impact and benchmark operation

> **What you'll learn:** Learn about QA review, release-impact advisories, technical retention and synthetic benchmarks.

**On this page:** [Testing](#testing)

---


**Engineering alpha only.** Synthetic data; no patient data, no FDA certification, no GxP electronic-signature claim. All outcomes are technical observations, and release/qualification approval remains with an authorized human quality process.

## #4 — Controlled deviation review and QMS transfer

Existing system registry, protocol baselines, run results, deviation and CAPA workflow are retained. Newly added `healthqualify/deviation_review.py` provides:
- QA-only review with **fresh password verification** against a local identity account
- Approved review categories: `RETEST_REQUIRED`, `ACCEPT_WITH_JUSTIFICATION`, `REJECTED` — none closes a deviation or qualifies the system
- Evidence link verified against the **original stored run** (`hq-run:<run-id>/test/<test-id>`)
- Review record bound to original run and protocol digests, with an audit event
- Offline, hashed JSON exchange package for a downstream QMS; it makes **no outgoing network calls**
- Evidence retention inventory with hold flag, retention date, exclusive-write artifact copy and checksum validation

Example after creating a local workspace and QA user via the existing `appcli bootstrap-admin` / `create-user` steps:

```bash
python -m healthqualify.quality_cli --db demo.db review-deviation \
  qa_user <deviation-id> RETEST_REQUIRED "Verify synthetic identity mapping" \
  "hq-run:<original-run-id>/test/OQ-001"
# Interactive prompt: QA password

python -m healthqualify.quality_cli --db demo.db qms-export <deviation-id> --out /tmp/qms-package.json

python -m healthqualify.quality_cli retain /tmp/qms-package.json qms_handoff \
  --folder /tmp/hq-vault --days 730 --legal-hold
python -m healthqualify.quality_cli retention-verify <record-id> --folder /tmp/hq-vault
```

**Limitations:** SQLite and the filesystem are not independently immutable. Retention and hold are metadata, not OS-enforced legal retention. A QMS transfer package is **not** a validated bidirectional vendor connector; site deployment must establish a controlled integration mapping, TLS, identity and audit controls, reconciliation and qualified human sign-off. Review categories are QA records, not electronic signatures.

## #6 — Release-triggered impact plans with human review

`.github/workflows/release-qualification.yml` runs on a **published GitHub Release** or explicit manual dispatch using an existing tag. Full Git history is checked out. It resolves the tagged commit and nearest prior release tag, uses a bounded Git diff, and proposes test reruns through the existing conservative component map.

- Known mapped files → `REVIEW_REQUIRED`, targeted test recommendations.
- Unmapped files or no previous tag → `UNKNOWN_IMPACT`, **all protocol tests** recommended.
- A no-change diff still requires human review.
- Every plan has `qualification_approved: false`.
- Workflow uploads `qualification-impact-advisory` as a **30-day GitHub Actions artifact**; uploading is not a release authorization.

A local QA reviewer can record a credential-verified `ACKNOWLEDGED`, `RETEST_REQUIRED`, or `BLOCKED` decision against the exact SHA-bound impact plan. No `APPROVED` state exists in this workflow:

```bash
python -m healthqualify.quality_cli --db demo.db release-plan \
  examples/synthetic_lis_v3/protocol.json <40-char-base-sha> <40-char-head-sha> \
  --out /tmp/release-plan.json

python -m healthqualify.quality_cli --db demo.db release-review \
  /tmp/release-plan.json qa_user RETEST_REQUIRED "Verify changes to laboratory interfaces"
```

**Limitations:** Source-path mappings are manually declared, not proven complete by dependency analysis. Unknown dependencies produce conservative full-test recommendations. Tags and release events should be protected by repository policies not configured here. Reviewer decision records live in the local SQLite demonstration store, not a validated e-signature/audit service. This workflow never changes a deployment, merge or release permission.

## #9 — Reproducible equal-input benchmark

The benchmark exercises the **identical versioned synthetic LIS protocol and fixtures** for:

1. HealthQualify deterministic engine.
2. Independently authored Python standard-library test executor and requirement-to-result coverage matrix.
3. Plain pytest assertions over the same seven protocol cases, with a JUnit result artifact generated internally.

The benchmark counts PASS/FAIL/ERROR/NOT_RUN, seeded defect detection, basic requirement-link availability, and runtime median over three repetitions. It records the source protocol SHA-256, **does not claim superiority**, and explicitly distinguishes pytest process-startup overhead. `setup_effort` and `maintenance_effort` remain `NOT_MEASURED`: using synthetic measurements to assert their human cost would be misleading.

```bash
python -m pip install 'pytest>=8,<10'
python -m benchmarks.compare --repetitions 3 --out benchmark-results.json
```

The `Equal-input synthetic benchmark` workflow runs on every push to `main` and by manual dispatch, publishing `benchmark-results.json` as the artifact `healthqualify-equal-input-benchmark` for 90 days. It reports reproducible **runner observations**, not an independent laboratory evaluation. Cross-project setup/maintenance experiments and external validation are still required before claiming superiority.

## Testing

```bash
python -m pip install -r requirements-security.txt
python -m pip install 'pytest>=8,<10'
python -m unittest discover -s tests -v
```

The intentionally seeded LIS failures are expected: two passing cases and five failing cases. Production/live clinical and regulated electronic record workflows remain out of scope.

---

### Continue exploring

[release status](RELEASE_STATUS.md) · [roadmap](ROADMAP.md) · [All guides](README.md) · [Project homepage](../README.md)
