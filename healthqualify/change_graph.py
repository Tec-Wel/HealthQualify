"""Conservative source path to qualification test mapping.

Unmapped or ambiguous changes cause UNKNOWN_IMPACT, never green-light a release.
"""
from __future__ import annotations
from pathlib import PurePosixPath
from .protocol_v3 import validate_v3

def normalize(path):
    if not isinstance(path,str) or not path or path.startswith("/") or "\\" in path:
        raise ValueError("Only repository-relative paths accepted")
    parts=PurePosixPath(path).parts
    if ".." in parts or "." in parts or any(p=="" for p in parts):
        raise ValueError("Unsafe changed path")
    return str(PurePosixPath(*parts))

def plan_requalification(protocol, changed_paths):
    validate_v3(protocol)
    if not isinstance(changed_paths,list) or not changed_paths or len(changed_paths)>1000:
        raise ValueError("Nonempty bounded changed-files list required")
    changed=set(normalize(p) for p in changed_paths)
    affected=set()
    unknown=set(changed)
    for test in protocol["tests"]:
        for component in test["component_paths"]:
            prefix=normalize(component).rstrip("/")
            matched={p for p in changed if p==prefix or p.startswith(prefix+"/")}
            if matched:
                unknown.difference_update(matched)
                affected.add(test["id"])
    if unknown:
        # Conservative fallback: all current tests, not just mapped ones.
        affected.update(t["id"] for t in protocol["tests"])
    return {"impact":"UNKNOWN_IMPACT" if unknown else "REVIEW_REQUIRED",
            "changed_paths":sorted(changed),
            "unmapped_paths":sorted(unknown),
            "recommended_test_ids":sorted(affected),
            "human_review_required":True,
            "qualification_approved":False}
