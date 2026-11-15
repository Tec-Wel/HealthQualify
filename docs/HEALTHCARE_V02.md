# v0.2 Synthetic Healthcare Qualification Guide

## Scope
HealthQualify v0.2 is **a local offline example**, not a validated clinical integration, formal IQ/OQ/PQ qualification system, a GAMP assessment, or an electronic-signature solution.

It implements the product's initial independent execution model using synthetic values only. There are no third-party dependencies, model calls, network calls, arbitrary commands, or database connections.

## What gets exercised
- **IQ:** release identifier matches a declared baseline.
- **OQ/HL7:** PID-3 patient identifier and OBX-6 observation units match a specified synthetic contract.
- **OQ/authorization:** a cross-tenant request is denied.
- **OQ/notification:** a critical-result notification was delivered.
- **OQ/FHIR:** a JSON resource has the expected resourceType.
- **PQ demonstration:** an audit event exists (not sufficient as a real-world PQ).

The synthetic profile purposefully produces **five failures** and two passes. It validates checks and reporting, not patient safety or a hospital system.

## Commands
```bash
python -m healthqualify.cli validate-v2 examples/synthetic_lis_v2/protocol.json

# Expect exit status 1 because five deliberate failures are found
python -m healthqualify.cli run-v2 examples/synthetic_lis_v2/protocol.json --out .healthqualify/v2-run

# Verify local bundle hashes; this alone does NOT establish authorship or immutable evidence
python -m healthqualify.cli verify-v2 .healthqualify/v2-run

python -m unittest discover -s tests -v
```

The run prints a manifest digest. Store it independently, then verify with `--trusted-manifest-sha256 <digest>` when checking the bundle.

## Evidence schema
- `protocol.json`: original draft synthetic protocol bytes.
- `results.json`: actual check statuses, observations, requirement traceability, uncovered requirements, findings, run time and explicit `qualification_approved: false`.
- `manifest.json`: hashes of protocol and results plus explicit unsigned warning.

## Trust and source attribution
- Requirement `acceptance_basis` is **a supplied description**, not proof of formal approval.
- The runner does not set any regulated approval state and rejects `qualification_state: approved`.
- Any mismatch in required artifact hashes fails verification.
- A malicious party who controls **both** artifacts and the manifest can rewrite all three; use an independently trusted digest today, and signed/protected evidence storage in subsequent releases.
- Missing expected values or absent acceptance basis prevent execution.
- Missing fixtures become NOT_RUN; malformed HL7 becomes ERROR.
- Unmapped requirements become UNCOVERED and do not count as qualified.

## Roadmap for actual healthcare adoption
1. Convert the fixture-only adapters into isolated, authorized read-only integration adapters, with schema/profile-aware FHIR/HL7 validation and negative-path test fixtures.
2. Implement formal protocol versioning and identity-backed approval workflows. Never infer a clinical acceptance threshold.
3. Add environment fingerprints, worker attestation, independently timestamped/signed manifests, retention and role-based access control.
4. Provide hospital software assurance and GxP qualification profiles selected after applicability review.
5. Support human-witnessed PQ and workflow-specific tests, beyond API-level assertions.
6. Validate the tool itself under the intended quality-system process before regulated operational reliance.

## Independent development
Implementation is original HealthQualify code informed by general functionality of ParaQualis and medtest-traceability. Neither upstream codebase is forked or copied.
