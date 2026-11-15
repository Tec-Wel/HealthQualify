# Release impact and review — TEMPLATE

**Advisory engineering worksheet; NEVER an automatic release approval.**

| Field | Entry |
| --- | --- |
| Release/tag | __________________ |
| Base full Git SHA | __________________ |
| Head full Git SHA | __________________ |
| Protocol SHA-256 | __________________ |
| Impact category | REVIEW_REQUIRED / UNKNOWN_IMPACT / NO_CHANGED_FILES |
| Mapped changed files | __________________ |
| Unmapped changed files | __________________ |
| Suggested tests | __________________ |
| Tests actually executed (and justification) | __________________ |
| FAIL / ERROR / NOT_RUN | __________________ |
| New evidence manifest trusted digest | __________________ |
| Deviation/CAPA references | __________________ |
| Human review decision | ACKNOWLEDGED / RETEST_REQUIRED / BLOCKED |
| External controlled release approval | PENDING, not a HealthQualify decision |

## Review prompts
Were dependencies or configuration changes omitted from mappings? Were any tests skipped? Did interface contracts change? Is the environment representative? Was evidence independently verified and retained? Who is responsible for a formal release disposition?
