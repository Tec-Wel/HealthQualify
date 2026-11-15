"""Conservative qualification drift review; no automated release approvals."""
from __future__ import annotations

from .assurance import validate_v2


def compare_protocols(before: dict, after: dict) -> dict:
    """Compare two draft profiles; unknown links always require reviewer assessment."""
    validate_v2(before)
    validate_v2(after)
    if before["system"]["id"] != after["system"]["id"]:
        raise ValueError("Cannot compare different system ids")
    oldreq = {x["id"]: x for x in before["requirements"]}
    newreq = {x["id"]: x for x in after["requirements"]}
    oldtests = {x["id"]: x for x in before["tests"]}
    newtests = {x["id"]: x for x in after["tests"]}
    changed_req = sorted(rid for rid in oldreq.keys() | newreq.keys() if oldreq.get(rid) != newreq.get(rid))
    changed_tests = sorted(tid for tid in oldtests.keys() | newtests.keys() if oldtests.get(tid) != newtests.get(tid))
    environment_changed = before["system"] != after["system"]
    fixtures_changed = before["fixtures"] != after["fixtures"]
    impacted_tests = set(changed_tests)
    for test in after["tests"]:
        if any(rid in changed_req for rid in test["requirement_ids"]):
            impacted_tests.add(test["id"])
    # The fixture and execution environment cannot be treated as safe without
    # verified component-level provenance. Treat any such drift as unknown.
    unknown = environment_changed or fixtures_changed
    if unknown:
        impacted_tests.update(newtests)
    return {
        "system_id": after["system"]["id"], "from_version": before["system"]["version"],
        "to_version": after["system"]["version"],
        "requirements_changed": changed_req, "tests_changed": changed_tests,
        "environment_changed": environment_changed, "fixtures_changed": fixtures_changed,
        "recommended_test_ids": sorted(impacted_tests),
        "impact": "UNKNOWN_IMPACT" if unknown else ("REVIEW_REQUIRED" if impacted_tests else "NO_DECLARED_CHANGE"),
        "human_review_required": bool(impacted_tests or unknown),
        "qualification_approved": False,
        "notice": "Static protocol comparison only; cannot prove unchanged implementation behavior."
    }
