"""Data-minimal persisted qualification records.

Technical PASS/FAIL outcomes and source links remain. Raw synthetic/healthcare
observations are not stored in workspace result records by default.
"""
from __future__ import annotations
from copy import deepcopy

def minimize_result(report: dict) -> dict:
    copy=deepcopy(report)
    for entry in copy.get("results",[]):
        if "actual" in entry:
            entry["actual"]="[WITHHELD]"
        if "expected" in entry:
            entry["expected"]="[WITHHELD]"
        if "detail" in entry and len(str(entry["detail"]))>200:
            entry["detail"]="[DETAIL_WITHHELD]"
    copy["privacy_policy"]="Evidence observation values withheld from workspace result records"
    copy["qualification_approved"]=False
    return copy

GATES = {
 "identity_proofing":"Formal identity lifecycle and approved MFA/SSO",
 "authorization_review":"Role matrix and independent penetration testing",
 "evidence_controls":"Protected storage, retention, backup/restore, signature verification",
 "audit_integrity":"Append-only independently trusted audit records",
 "e_signature_assessment":"Documented Part 11 or applicable e-signature review and qualification",
 "privacy_impact":"Data minimization, lawful basis and privacy impact assessment",
 "healthcare_interfaces":"Site-approved authenticated endpoint and integration qualification",
 "clinical_acceptance":"Approved intended-use test criteria and witnessed performance",
 "software_assurance":"HealthQualify itself validated to defined intended use",
 "operational_security":"TLS, key management, patching, monitoring, incident response",
}

def release_readiness(evidence: dict | None = None) -> dict:
    evidence=evidence or {}
    status={}
    for key,label in GATES.items():
        ref=evidence.get(key)
        status[key]={"requirement":label,"status":"REVIEW_REQUIRED",
                     "evidence_reference":ref if isinstance(ref,str) and ref.strip() else None}
    return {"product":"HealthQualify","technical_release_gate":"BLOCKED",
            "criteria":status,"qualifier":"Only an authorized human quality/security review can resolve gates.",
            "regulated_use_approved":False}
