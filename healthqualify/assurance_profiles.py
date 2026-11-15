"""Explicit risk-based assurance planning; source citations, not compliance verdicts."""
from __future__ import annotations
from .regulatory import CATALOG

def plan(system, controls, selected, reviewer=None):
    if not isinstance(system,dict) or not system.get("intended_use"):
        raise ValueError("System intended use required")
    if selected not in ("IQ-OQ-PQ", "CSA"):
        raise ValueError("Choose IQ-OQ-PQ or CSA")
    if not isinstance(controls,dict) or not controls or any(
        k not in CATALOG or v not in ("APPLICABLE","NOT_APPLICABLE","UNDETERMINED")
        for k,v in controls.items()
    ):
        raise ValueError("Explicit framework applicability assessment required")
    return {"assurance_pathway":selected, "system":system,
            "controls":[{"id":k,"classification":CATALOG[k]["kind"],
                         "applicability":v,"source":CATALOG[k]["source"]}
                        for k,v in controls.items()],
            "risk_method":"intended-use and process-risk review required",
            "testing_modes":["scripted","manual","exploratory"] if selected=="CSA"
                            else ["IQ","OQ","PQ","manual"],
            "reviewer":reviewer,"approval":"DRAFT",
            "legal_determination":False,
            "warning":"Profiles guide planning; licensed standards are not reproduced."}
