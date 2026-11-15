# Qualification issue hardening: replay integrity and PR impact

## Current engineering changes

1. Evidence receipts created by the offline synthetic v0.3 runner are now verified against a second deterministic execution of the exact protocol. This detects forged PASS results even if someone rehashes the manifest, **provided the verifier itself and source implementation are trusted**.
2. GitHub pull requests now run a conservative change-impact analyzer based on the PR base commit's Git SHA. Mapped changes produce a recommended test list; unmapped files produce `UNKNOWN_IMPACT` and all tests.
3. The analyzer writes its recommendations into the GitHub Actions job summary. This is **advisory**, never a qualification approval, and does not claim that all dependencies were discovered.
4. Unit tests cover forged receipts, tampered evidence, mapped and unmapped changes, empty diffs, and unsafe base refs.

## What this does not establish

- An attacker controlling the code, verifier, trust anchors or filesystem may still produce misleading evidence.
- Successful CI does not imply completed IQ/OQ/PQ, CSA, or regulatory compliance.
- An impact plan is only as reliable as the source-to-test mappings; unknown changes always require reviewer attention.
- Protected evidence storage, real-source integration qualification, licensed regulatory review, customer-specific approvals and independent verification remain open work.

The nine original issues should be closed individually only when their full original acceptance criteria are demonstrably satisfied, not because a CI job is green.
