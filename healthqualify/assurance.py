"""HealthQualify protocol v0.2: standalone, no-AI qualification assessment.

The engine executes only predefined assertions against embedded synthetic fixtures.
It is not a validated GxP software system or an electronic approval mechanism.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .healthcare import CheckError, observe

CHECKS = {"equals", "present", "hl7_field_equals", "fhir_field_equals", "role_denied"}
PHASES = {"IQ", "OQ", "PQ"}
RISK_LEVELS = {"low", "medium", "high", "critical"}
STATUSES = ("PASS", "FAIL", "ERROR", "NOT_RUN")


def encode(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, explanation: str) -> None:
    if not condition:
        raise ValueError(explanation)


def validate_v2(doc: Any) -> None:
    require(isinstance(doc, dict), "Protocol must be a JSON object")
    require(doc.get("schema_version") == "0.2", "schema_version must be 0.2")
    system = doc.get("system")
    require(isinstance(system, dict) and all(isinstance(system.get(k), str) and system[k]
        for k in ("id", "version", "intended_use", "environment")), "System identification incomplete")
    require(system["environment"] == "synthetic", "v0.2 permits synthetic environment only")
    require(doc.get("qualification_state") == "draft", "v0.2 accepts draft protocols only; no electronic approvals supported")
    requirements = doc.get("requirements")
    require(isinstance(requirements, list) and bool(requirements), "Nonempty requirements required")
    req_ids = set()
    for req in requirements:
        require(isinstance(req, dict) and isinstance(req.get("id"), str) and bool(req["id"]), "Requirement id required")
        require(req["id"] not in req_ids, "Duplicate requirement id")
        req_ids.add(req["id"])
        require(req.get("risk") in RISK_LEVELS, "Requirement risk level required")
        require(isinstance(req.get("acceptance_basis"), str) and bool(req["acceptance_basis"].strip()),
                "Documented source of acceptance criteria required")
    tests = doc.get("tests")
    require(isinstance(tests, list) and bool(tests), "Nonempty tests required")
    require(isinstance(doc.get("fixtures"), dict), "Synthetic fixtures object required")
    test_ids = set()
    for case in tests:
        require(isinstance(case, dict) and isinstance(case.get("id"), str) and bool(case["id"]), "Test id required")
        require(case["id"] not in test_ids, "Duplicate test id")
        test_ids.add(case["id"])
        require(case.get("phase") in PHASES, "Unsupported phase")
        require(case.get("check") in CHECKS, "Unsupported check")
        require(isinstance(case.get("fixture"), str) and bool(case["fixture"]), "Fixture name required")
        links = case.get("requirement_ids")
        require(isinstance(links, list) and bool(links) and all(isinstance(x, str) and x in req_ids for x in links),
                "Every test must link to an existing requirement")
        if case["check"] in {"equals", "hl7_field_equals", "fhir_field_equals"}:
            require("expected" in case and case["expected"] is not None, "Explicit expected value required")
        if case["check"] == "hl7_field_equals":
            require(case.get("segment") in {"PID", "OBR", "OBX", "MSH"},
                    "Allowlisted HL7 segment required")
            require(type(case.get("field_index")) is int and 1 <= case["field_index"] <= 30,
                    "HL7 field index must be between 1 and 30")
        if case["check"] == "fhir_field_equals":
            require(isinstance(case.get("path"), str) and case["path"] and len(case["path"]) < 180,
                    "FHIR path required")
    require(len(encode(doc)) <= 1024 * 1024, "Protocol size exceeds 1 MB")


def assess_v2(doc: dict) -> dict:
    validate_v2(doc)
    results = []
    for case in doc["tests"]:
        name = case["fixture"]
        if name not in doc["fixtures"]:
            status, actual, detail = "NOT_RUN", None, "Synthetic fixture missing"
        else:
            try:
                passed, actual = observe(case["check"], doc["fixtures"][name], case)
                status = "PASS" if passed else "FAIL"
                detail = "Assertion satisfied" if passed else "Observed value differs from acceptance criteria"
            except (CheckError, TypeError, ValueError, KeyError) as err:
                status, actual, detail = "ERROR", None, str(err)
        results.append({
            "id": case["id"], "phase": case["phase"], "requirement_ids": case["requirement_ids"],
            "fixture": name, "check": case["check"], "expected": case.get("expected"),
            "actual": actual, "status": status, "detail": detail
        })
    traceability = []
    gaps = []
    for requirement in doc["requirements"]:
        linked = [r for r in results if requirement["id"] in r["requirement_ids"]]
        if not linked:
            state = "NOT_RUN"
            gaps.append({"requirement_id": requirement["id"], "kind": "UNCOVERED", "risk": requirement["risk"]})
        else:
            states = {r["status"] for r in linked}
            state = next((s for s in ("FAIL", "ERROR", "NOT_RUN") if s in states), "PASS")
        traceability.append({
            "requirement_id": requirement["id"], "risk": requirement["risk"],
            "test_ids": [r["id"] for r in linked], "status": state,
            "acceptance_basis": requirement["acceptance_basis"]
        })
    for r in results:
        if r["status"] != "PASS":
            gaps.append({"test_id": r["id"], "kind": r["status"],
                         "requirement_ids": r["requirement_ids"], "detail": r["detail"]})
    return {
        "schema_version": "0.2", "system": doc["system"], "qualification_state": "draft",
        "executed_at_utc": datetime.now(timezone.utc).isoformat(), "results": results,
        "traceability": traceability, "gaps": gaps,
        "summary": {s: sum(1 for r in results if r["status"] == s) for s in STATUSES},
        "qualification_approved": False,
        "notice": "Synthetic engineering observations; not clinical, regulatory or formal qualification approval."
    }


def save_v2(protocol: bytes, destination: Path) -> dict:
    doc = json.loads(protocol)
    result = assess_v2(doc)
    destination.mkdir(parents=True, exist_ok=False)
    files = {"protocol.json": protocol, "results.json": encode(result)}
    for filename, content in files.items():
        (destination / filename).write_bytes(content)
    manifest = {
        "schema_version": "0.2",
        "hash": "sha256",
        "files": {name: digest(data) for name, data in files.items()},
        "warning": "Unsigned manifest. Verify against separately trusted digest for tamper detection."
    }
    (destination / "manifest.json").write_bytes(encode(manifest))
    return result


def verify_v2(directory: Path, trusted_sha256: str | None = None) -> bool:
    raw = (directory / "manifest.json").read_bytes()
    if trusted_sha256 is not None and digest(raw) != trusted_sha256:
        return False
    manifest = json.loads(raw)
    if manifest.get("schema_version") != "0.2" or manifest.get("hash") != "sha256":
        return False
    files = manifest.get("files")
    if not isinstance(files, dict) or set(files) != {"protocol.json", "results.json"}:
        return False
    if not all(isinstance(v, str) and len(v) == 64 for v in files.values()):
        return False
    if not all((directory / name).is_file() and digest((directory / name).read_bytes()) == checksum
               for name, checksum in files.items()):
        return False
    doc = json.loads((directory / "protocol.json").read_bytes())
    result = json.loads((directory / "results.json").read_bytes())
    validate_v2(doc)
    return (result.get("schema_version") == "0.2" and result.get("qualification_approved") is False
            and result.get("system") == doc.get("system"))
