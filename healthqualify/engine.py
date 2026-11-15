"""Deterministic, synthetic-data-only reference qualification engine.

This alpha intentionally restricts checks to declarative equality and presence
against embedded synthetic fixtures. It does not run arbitrary commands, query
production databases, send network requests, or claim regulatory qualification.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ALLOWED_PHASES = {"IQ", "OQ", "PQ"}
ALLOWED_CHECKS = {"equals", "present"}
STATUSES = {"PASS", "FAIL", "ERROR", "NOT_RUN"}


def canonical_json(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate(protocol: dict) -> None:
    if not isinstance(protocol, dict):
        raise ValueError("Protocol must be a JSON object")
    if not isinstance(protocol.get("system"), dict):
        raise ValueError("system must be an object")
    if not isinstance(protocol.get("requirements"), list) or not protocol["requirements"]:
        raise ValueError("requirements must be a nonempty array")
    if not isinstance(protocol.get("tests"), list) or not protocol["tests"]:
        raise ValueError("tests must be a nonempty array")
    req_ids = []
    for req in protocol["requirements"]:
        if not isinstance(req, dict) or not isinstance(req.get("id"), str) or not req["id"]:
            raise ValueError("Every requirement needs an id")
        req_ids.append(req["id"])
    if len(set(req_ids)) != len(req_ids):
        raise ValueError("Duplicate requirement ids")
    test_ids = []
    for t in protocol["tests"]:
        if not isinstance(t, dict) or not isinstance(t.get("id"), str) or not t["id"]:
            raise ValueError("Every test needs an id")
        test_ids.append(t["id"])
        if t.get("phase") not in ALLOWED_PHASES:
            raise ValueError("Unknown qualification phase")
        if t.get("check") not in ALLOWED_CHECKS:
            raise ValueError("Unsupported check")
        if not isinstance(t.get("requirement_ids"), list) or not t["requirement_ids"]:
            raise ValueError("Test must link to requirements")
        if any(x not in req_ids for x in t["requirement_ids"]):
            raise ValueError("Test links to unknown requirement")
        if not isinstance(t.get("fixture"), str) or not t["fixture"]:
            raise ValueError("Test fixture key required")
        if t["check"] == "equals" and "expected" not in t:
            raise ValueError("equals requires approved expected value")
    if len(set(test_ids)) != len(test_ids):
        raise ValueError("Duplicate test ids")
    if not isinstance(protocol.get("fixtures"), dict):
        raise ValueError("fixtures must be a JSON object")


def execute(protocol: dict) -> dict:
    validate(protocol)
    fixtures = protocol["fixtures"]
    outcomes = []
    for t in protocol["tests"]:
        key = t["fixture"]
        if key not in fixtures:
            status, actual, message = "NOT_RUN", None, "Synthetic fixture unavailable"
        else:
            actual = fixtures[key]
            try:
                match = (actual == t["expected"]) if t["check"] == "equals" else (actual is not None)
                status = "PASS" if match else "FAIL"
                message = "Acceptance check satisfied" if match else "Observed value failed acceptance check"
            except (TypeError, ValueError) as exc:
                status, message = "ERROR", type(exc).__name__
        outcomes.append({
            "id": t["id"], "phase": t["phase"], "requirement_ids": t["requirement_ids"],
            "check": t["check"], "fixture": key, "expected": t.get("expected"),
            "actual": actual, "status": status, "message": message,
        })
    trace = []
    for req in protocol["requirements"]:
        linked = [o for o in outcomes if req["id"] in o["requirement_ids"]]
        statuses = [o["status"] for o in linked]
        overall = ("NOT_RUN" if not linked else
                   "FAIL" if "FAIL" in statuses else
                   "ERROR" if "ERROR" in statuses else
                   "NOT_RUN" if "NOT_RUN" in statuses else "PASS")
        trace.append({"requirement_id": req["id"], "test_ids": [o["id"] for o in linked], "status": overall})
    summary = {s: sum(o["status"] == s for o in outcomes) for s in sorted(STATUSES)}
    return {"system": protocol["system"], "results": outcomes, "traceability": trace,
            "summary": summary, "qualification_approved": False,
            "notice": "Technical checks only; qualified human approval not provided."}


def save_run(protocol_bytes: bytes, output: Path) -> dict:
    protocol = json.loads(protocol_bytes)
    result = execute(protocol)
    output.mkdir(parents=True, exist_ok=False)
    artifacts = {"protocol.json": protocol_bytes, "results.json": canonical_json(result)}
    for name, data in artifacts.items():
        (output / name).write_bytes(data)
    manifest = {"schema_version": "0.1", "artifacts": {name: sha256(data) for name, data in artifacts.items()},
                "disclaimer": "Unsigned hashes only; not a regulated immutable evidence store."}
    (output / "manifest.json").write_bytes(canonical_json(manifest))
    return result


def verify_run(output: Path) -> bool:
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    artifacts = manifest["artifacts"]
    if sorted(artifacts) != ["protocol.json", "results.json"]:
        return False
    return all((output / name).is_file() and sha256((output / name).read_bytes()) == digest
               for name, digest in artifacts.items())
