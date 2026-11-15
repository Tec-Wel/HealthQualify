# Deviation / investigation / retest — TEMPLATE

> Synthetic example; no legal e-signature or formal QMS approval is generated.

| Field | Entry |
| --- | --- |
| Deviation ID | DEV-SYNTH-001 |
| System, version, environment | Synthetic LIS, 0.2, local |
| Requirement/test | URS-002 / OQ-001 |
| Observed failure | Synthetic PID-3 does not match criterion |
| Original run ID/evidence digest | ____________________ |
| Impact/risk and scope | Assess identity mapping and related tests |
| Immediate containment | Do not treat result as passing |
| Suspected root cause | Pending engineering investigation |
| Confirmed root cause/evidence | ____________________ |
| Corrective action + owner | ____________________ |
| Verification action and retest ID | **New** run directory, never overwrite original |
| Effectiveness evidence | ____________________ |
| Independent QA review | PENDING |
| Final status | OPEN (demonstration) |

## Disposition rationale
Why was the chosen action justified? What evidence demonstrates the change? Are other risks affected? What external QMS record will preserve the decision?

## Integrity and provenance
Record original and corrected build SHAs, protocol digests, original/trusted manifest digests, reviewer, timestamp source and the independent storage path. A `quality_cli review-deviation` record **does not close** the deviation.
