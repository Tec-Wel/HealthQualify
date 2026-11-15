"""Strict v0.3 synthetic protocol contract and deterministic test policy.

No migration of previously baselined protocols occurs automatically. The extra
metadata is assessed, but never construed as a regulated approval.
"""
from __future__ import annotations
from copy import deepcopy
from .assurance import validate_v2, assess_v2, digest, encode

TOP = {"schema_version", "qualification_state", "system", "requirements",
       "tests", "fixtures", "execution_policy", "source_references", "approval_reference"}
SYSTEM = {"id", "name", "version", "environment", "intended_use", "build_sha"}
REQ = {"id", "risk", "acceptance_basis", "source_id"}
TEST = {"id", "phase", "check", "fixture", "requirement_ids",
        "expected", "segment", "field_index", "path", "component_paths"}
POLICY = {"network", "allow_ai", "destructive", "data_classification", "runner_version"}
CLASSES = {"synthetic", "public"}

def _keys(obj, accepted, location):
    if not isinstance(obj, dict):
        raise ValueError(location + " must be a mapping")
    unknown = set(obj) - accepted
    if unknown:
        raise ValueError(location + " contains unknown fields: " + ", ".join(sorted(unknown)))

def validate_v3(doc):
    _keys(doc, TOP, "protocol")
    if doc.get("schema_version") != "0.3":
        raise ValueError("Expected schema_version 0.3")
    if doc.get("qualification_state") != "draft":
        raise ValueError("Regulated approval is not supported")
    _keys(doc.get("system"), SYSTEM, "system")
    if not isinstance(doc["system"].get("build_sha"), str) or len(doc["system"]["build_sha"]) != 40:
        raise ValueError("A full 40-character build_sha is required")
    _keys(doc.get("execution_policy"), POLICY, "policy")
    policy = doc["execution_policy"]
    if policy.get("network") is not False or policy.get("destructive") is not False or policy.get("allow_ai") is not False:
        raise ValueError("v0.3 synthetic runner must disable network, AI and destructive actions")
    if policy.get("data_classification") not in CLASSES:
        raise ValueError("Unapproved data classification")
    if not isinstance(policy.get("runner_version"), str) or not policy["runner_version"]:
        raise ValueError("Runner version required")
    refs = doc.get("source_references")
    if not isinstance(refs, dict) or not refs:
        raise ValueError("Nonempty source reference registry required")
    if any(not isinstance(k,str) or not k or not isinstance(v,str) or not v.strip() for k,v in refs.items()):
        raise ValueError("Invalid source reference registry")
    if doc.get("approval_reference") is not None:
        raise ValueError("Draft synthetic protocol cannot declare a formal approval")
    for req in doc.get("requirements", []):
        _keys(req, REQ, "requirement")
        if req.get("source_id") not in refs:
            raise ValueError("Requirement missing source registry linkage")
    for test in doc.get("tests", []):
        _keys(test, TEST, "test")
        paths = test.get("component_paths")
        if not isinstance(paths,list) or not paths or any(
            not isinstance(p,str) or not p.strip() or p.startswith("/") or ".." in p or "\\" in p for p in paths
        ):
            raise ValueError("Each test needs safe repository-relative component paths")
    legacy = deepcopy(doc)
    legacy["schema_version"] = "0.2"
    for name in ("execution_policy", "source_references", "approval_reference"):
        legacy.pop(name, None)
    for x in legacy["requirements"]:
        x.pop("source_id", None)
    for x in legacy["tests"]:
        x.pop("component_paths", None)
    validate_v2(legacy)
    return legacy

def execute_v3(doc):
    legacy = validate_v3(doc)
    result = assess_v2(legacy)
    result["schema_version"] = "0.3"
    result["protocol_sha256"] = digest(encode(doc))
    result["runner_version"] = doc["execution_policy"]["runner_version"]
    result["build_sha"] = doc["system"]["build_sha"]
    result["execution_policy"] = deepcopy(doc["execution_policy"])
    result["source_references"] = deepcopy(doc["source_references"])
    result["qualification_approved"] = False
    return result
