"""Five offline, read-only qualification investigators for v0.3 synthetic protocols.

These agents produce advisory findings only. They never execute tests, approve
protocols, update quality records, or use a remote LLM. Qwen is opt-in and only
explains deterministic findings; it cannot replace them.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .ai import local_draft
from .change_graph import normalize, plan_requalification
from .evidence_v3 import verify_v3
from .protocol_v3 import validate_v3

AGENTS = ("release-impact", "gap-hunter", "failure-investigation",
          "qa-readiness", "dependency-investigator")
MAX_BYTES = 1024 * 1024
MAX_COMPONENTS = 1000
LLM_ROLES = {
    "release-impact": "requirements",
    "gap-hunter": "requirements",
    "failure-investigation": "deviation",
    "qa-readiness": "requirements",
    "dependency-investigator": "requirements",
}


def _load_json(path: str | Path) -> dict:
    p = Path(path)
    if not p.is_file() or p.stat().st_size > MAX_BYTES:
        raise ValueError("Missing or oversized JSON input (limit 1 MiB)")
    obj = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("JSON input must be an object")
    return obj


def _finding(code: str, severity: str, message: str, refs: list[str]) -> dict:
    return {"code": code, "severity": severity, "message": message,
            "source_refs": sorted(set(refs))}


def _evidence(path: str | None, trusted_sha: str | None, protocol: dict):
    if bool(path) != bool(trusted_sha):
        raise ValueError("Evidence directory and independent trusted digest required together")
    if not path:
        return None
    if not verify_v3(Path(path), trusted_sha):
        raise ValueError("Evidence failed trusted manifest verification")
    evidence_protocol = _load_json(Path(path) / "protocol.json")
    from .assurance import digest, encode
    if digest(encode(protocol)) != digest(encode(evidence_protocol)):
        raise ValueError("Evidence belongs to a different protocol")
    result = _load_json(Path(path) / "results.json")
    return result


def _release(protocol: dict, changed_files: list[str]) -> tuple[dict, list[dict]]:
    if not changed_files:
        raise ValueError("Release impact requires explicit changed files")
    impact = plan_requalification(protocol, changed_files)
    findings = [
        _finding("IMPACT_REVIEW", "review", "Change impact requires human review",
                 ["protocol:tests"] + ["component:" + p for p in impact["changed_paths"]])
    ]
    if impact["unmapped_paths"]:
        findings.append(_finding(
            "UNKNOWN_IMPACT", "critical",
            "Unmapped changed components: " + ", ".join(impact["unmapped_paths"]),
            ["component:" + p for p in impact["unmapped_paths"]]))
    return {"impact": impact}, findings


def _gaps(protocol: dict, evidence: dict | None) -> tuple[dict, list[dict]]:
    by_req = {req["id"]: [] for req in protocol["requirements"]}
    for test in protocol["tests"]:
        for rid in test["requirement_ids"]:
            by_req[rid].append(test["id"])
    findings = []
    for req in protocol["requirements"]:
        rid = req["id"]
        if not by_req[rid]:
            findings.append(_finding("UNCOVERED", req["risk"],
                                     "Requirement has no mapped test",
                                     ["requirement:" + rid]))
    if evidence is None:
        findings.append(_finding("NO_VERIFIED_EXECUTION", "review",
                                 "No independently verified execution supplied; coverage is design-only",
                                 ["protocol:tests"]))
    else:
        by_id = {r["id"]: r for r in evidence["results"]}
        for test in protocol["tests"]:
            tid = test["id"]
            entry = by_id.get(tid)
            if entry is None or entry.get("status") not in ("PASS", "FAIL", "ERROR", "NOT_RUN"):
                findings.append(_finding("MISSING_RESULT", "critical",
                                         "No valid execution result for test " + tid,
                                         ["test:" + tid]))
            elif entry["status"] != "PASS":
                findings.append(_finding("TEST_" + entry["status"], "review",
                                         "Test " + tid + " recorded " + entry["status"],
                                         ["test:" + tid] + ["requirement:" + r for r in test["requirement_ids"]]))
    return {"requirements": len(by_req), "mapped_tests": sum(map(len, by_req.values())),
            "verified_execution_supplied": evidence is not None}, findings


def _failures(protocol: dict, evidence: dict | None) -> tuple[dict, list[dict]]:
    if evidence is None:
        return {"failure_count": None}, [_finding(
            "NO_VERIFIED_EXECUTION", "review",
            "Provide verified evidence to investigate execution failures", ["protocol:tests"])]
    failures = [r for r in evidence["results"] if r["status"] in ("FAIL", "ERROR", "NOT_RUN")]
    findings = [_finding("INVESTIGATE_" + r["status"], "review",
                         "Investigate observed " + r["status"] + " in test " + r["id"] +
                         "; root cause is not established",
                         ["test:" + r["id"]] + ["requirement:" + x for x in r["requirement_ids"]])
                for r in failures]
    return {"failure_count": len(failures), "failed_test_ids": [r["id"] for r in failures]}, findings


def _readiness(protocol: dict, evidence: dict | None) -> tuple[dict, list[dict]]:
    _, findings = _gaps(protocol, evidence)
    if evidence is not None:
        findings.append(_finding(
            "NO_QUALIFIED_APPROVAL", "review",
            "Synthetic protocol and evidence cannot establish formal quality approval",
            ["protocol:qualification_state"]))
    return {"readiness": "REVIEW_BLOCKED", "verified_execution_supplied": evidence is not None,
            "formal_approval_supported": False}, findings


def _dependencies(protocol: dict, changed_files: list[str],
                  registry: dict | None) -> tuple[dict, list[dict]]:
    if not changed_files:
        raise ValueError("Dependency investigation requires changed files")
    if registry is None:
        raise ValueError("Dependency investigation requires explicit local registry")
    systems = registry.get("systems")
    if not isinstance(systems, list) or len(systems) > MAX_COMPONENTS:
        raise ValueError("Registry systems must be a bounded list")
    changed = {normalize(p) for p in changed_files}
    affected = []
    mapped = set()
    seen = set()
    for system in systems:
        if not isinstance(system, dict) or not isinstance(system.get("id"), str) or not system["id"]:
            raise ValueError("Each registry system requires an id")
        if system["id"] in seen:
            raise ValueError("Duplicate system id")
        seen.add(system["id"])
        components = system.get("components")
        if not isinstance(components, list) or len(components) > MAX_COMPONENTS:
            raise ValueError("System components must be a bounded list")
        prefixes = [normalize(x) for x in components]
        hits = sorted({p for p in changed for c in prefixes if p == c or p.startswith(c + "/")})
        if hits:
            mapped.update(hits)
            affected.append({"system_id": system["id"], "changed_components": hits})
    unknown = sorted(changed - mapped)
    findings = [
        _finding("SYSTEM_IMPACT", "review", "Review affected system " + row["system_id"],
                 ["system:" + row["system_id"]] +
                 ["component:" + x for x in row["changed_components"]])
        for row in affected
    ]
    if unknown:
        findings.append(_finding("UNKNOWN_DEPENDENCY", "critical",
                                 "No registered system mapping for: " + ", ".join(unknown),
                                 ["component:" + x for x in unknown]))
    return {"affected_systems": affected, "unmapped_components": unknown,
            "dependency_review_required": True}, findings


def investigate(agent: str, protocol: dict, *, changed_files: list[str] | None = None,
                evidence_dir: str | None = None, trusted_manifest_sha256: str | None = None,
                registry: dict | None = None, use_ollama: bool = False,
                model: str = "qwen3:8b") -> dict:
    """Produce a bounded advisory report using already controlled local inputs.

    Optional Ollama output can only add an explanation, never alter findings.
    Caller must authorize inputs and storage; this is not a QMS approval API.
    """
    if agent not in AGENTS:
        raise ValueError("Unknown agent")
    validate_v3(protocol)
    if use_ollama and protocol["execution_policy"]["data_classification"] != "synthetic":
        raise ValueError("This alpha only sends synthetic input summaries to Ollama")
    evidence = _evidence(evidence_dir, trusted_manifest_sha256, protocol)
    changed_files = changed_files or []
    if agent == "release-impact":
        summary, findings = _release(protocol, changed_files)
    elif agent == "gap-hunter":
        summary, findings = _gaps(protocol, evidence)
    elif agent == "failure-investigation":
        summary, findings = _failures(protocol, evidence)
    elif agent == "qa-readiness":
        summary, findings = _readiness(protocol, evidence)
    else:
        summary, findings = _dependencies(protocol, changed_files, registry)
    from .assurance import digest, encode
    report = {
        "schema": "HQ-AGENT-DRAFT-0.1", "agent": agent,
        "system_id": protocol["system"]["id"],
        "protocol_sha256": digest(encode(protocol)),
        "status": "DRAFT_UNVERIFIED", "qualification_approved": False,
        "evidence": False, "human_review_required": True,
        "summary": summary, "findings": findings,
        "model_explanation": None,
        "notice": "Synthetic developer alpha. Findings are advisory, not qualification evidence or approval."
    }
    if use_ollama:
        # No fixture values, patient data, raw log text or arbitrary files in prompt.
        supplied = json.dumps({"agent": agent, "summary": summary, "findings": findings},
                              sort_keys=True, ensure_ascii=False)
        if len(supplied) > 11000:
            raise ValueError("Agent findings exceed bounded local AI context")
        response = local_draft(LLM_ROLES[agent], supplied, model, consent=True)
        report["model_explanation"] = {
            "model": model, "status": response["status"], "text": response["text"],
            "warning": "Unverified AI narrative. Deterministic findings above remain authoritative observations."
        }
    return report


def load_protocol(path: str | Path) -> dict:
    protocol = _load_json(path)
    validate_v3(protocol)
    return protocol


def load_registry(path: str | Path) -> dict:
    return _load_json(path)
