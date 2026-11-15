"""Human-review-first risk, requirements and protocol drafting.

Generated materials are drafts and contain NO automatically approved criteria.
"""
from __future__ import annotations
from copy import deepcopy
from .regulatory import CATALOG

def draft_urs(system: dict, stated_needs: list[dict]) -> dict:
    if not isinstance(system,dict) or not system.get("intended_use"):
        raise ValueError("Intended use required")
    if not isinstance(stated_needs,list) or not stated_needs:
        raise ValueError("At least one stated need required")
    requirements=[]
    for index,need in enumerate(stated_needs,1):
        if not isinstance(need,dict) or not need.get("statement"):
            raise ValueError("Each requirement needs source statement")
        if need.get("risk") not in {"low","medium","high","critical"}:
            raise ValueError("Requirement risk needs a valid level")
        requirements.append({
            "id":f"URS-{index:03d}","statement":str(need["statement"]),
            "risk":need["risk"],"source":need.get("source","user_stated"),
            "acceptance_basis":need.get("acceptance_basis"),
            "acceptance_state":"DEFINED_FOR_REVIEW" if need.get("acceptance_basis") else "TO_BE_DEFINED",
            "approval":"DRAFT"
        })
    return {"document_type":"URS","system":deepcopy(system),"requirements":requirements,
            "approval":"DRAFT","note":"Human review and acceptance criteria required before qualification execution."}

def risk_plan(system: dict, frameworks: list[str], criticality: str) -> dict:
    if not system.get("intended_use") or criticality not in {"low","medium","high","critical"}:
        raise ValueError("Intended use and criticality required")
    if not isinstance(frameworks,list) or any(k not in CATALOG for k in frameworks):
        raise ValueError("Unknown regulatory profile")
    return {
        "system":deepcopy(system),"frameworks":frameworks,"criticality":criticality,
        "assurance_pathways":["IQ/OQ/PQ","risk-based CSA"],
        "selected_pathway":None,"applicability":"REQUIRES_REVIEW",
        "recommended_work":[
            "Approve intended use and criticality",
            "Determine regulatory applicability with responsible quality team",
            "Identify critical requirements, acceptance criteria, and source references",
            "Select proportional scripted and witnessed checks",
            "Review executed evidence and open deviations before release"
        ],
        "qualification_approved":False
    }

def protocol_from_urs(urs: dict, system_id: str) -> dict:
    """Create empty test plan from requirements; never invent expected outcomes."""
    if urs.get("document_type")!="URS" or urs.get("approval")!="DRAFT":
        raise ValueError("Expected draft URS")
    if not isinstance(system_id,str) or not system_id:
        raise ValueError("System id required")
    requirements=[]
    for req in urs["requirements"]:
        basis=req.get("acceptance_basis")
        if basis:
            requirements.append({"id":req["id"],"risk":req["risk"],"acceptance_basis":basis})
    return {
        "schema_version":"0.2", "qualification_state":"draft",
        "system":{"id":system_id,"version":"DRAFT","intended_use":urs["system"]["intended_use"],
                  "environment":"synthetic"},
        "requirements":requirements,
        "tests":[], "fixtures":{},
        "planning_gaps":[
            {"requirement_id":x["id"],"issue":"acceptance criteria missing"} for x in urs["requirements"]
            if not x.get("acceptance_basis")
        ],
        "warning":"Not executable until test cases/fixtures are added and criteria are reviewed."
    }
