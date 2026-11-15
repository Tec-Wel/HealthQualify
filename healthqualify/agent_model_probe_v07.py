"""Explicitly opt-in real local Ollama inference acceptance probe.

This is NOT an automated clinical/regulated/model-accuracy validation. It
collects redacted synthetic explanations for a human rater. A model is never
allowed to change fixed deterministic findings or issue an approval.
"""
from __future__ import annotations
import argparse
import json
import re
import statistics
import time
from pathlib import Path
from .agents import investigate
from .ai import local_draft
from .assurance import encode, digest

ROOT=Path(__file__).resolve().parents[1]

def probe(model,*,consent=False,cases_file=None,protocol_file=None,max_cases=30):
    if consent is not True:
        raise ValueError("Real local inference requires explicit opt-in")
    if not isinstance(model,str) or not 1<=len(model)<=80:
        raise ValueError("Model name required")
    if type(max_cases) is not int or not 1<=max_cases<=30:
        raise ValueError("Bounded case count 1-30 required")
    cases_file=Path(cases_file or ROOT/"evaluations"/"agent_cases.json")
    protocol_file=Path(protocol_file or ROOT/"examples"/"synthetic_lis_v3"/"protocol.json")
    base=json.loads(protocol_file.read_text(encoding="utf-8"))
    cases=json.loads(cases_file.read_text(encoding="utf-8"))[:max_cases]
    measurements=[]
    for case in cases:
        import copy
        protocol=copy.deepcopy(base)
        if case.get("add_uncovered_requirement"):
            r=copy.deepcopy(protocol["requirements"][0])
            r["id"]="URS-EVAL-"+case["id"]
            protocol["requirements"].append(r)
        registry={"systems":[{"id":"LIS","components":["healthqualify/healthcare.py"]}]} if case["agent"]=="dependency-investigator" else None
        fixed=investigate(case["agent"],protocol,
                          changed_files=case.get("changed_files"),registry=registry)
        before=digest(encode({"summary":fixed["summary"],"findings":fixed["findings"]}))
        message=json.dumps({"agent":case["agent"],"summary":fixed["summary"],
                            "findings":fixed["findings"]},sort_keys=True)
        started=time.perf_counter()
        try:
            output=local_draft(case["agent"],message,model,consent=True)
            status="DRAFT_UNVERIFIED"
            narrative=output["text"]
            failure=None
        except Exception as exc:
            status="MODEL_ERROR"
            narrative=None
            failure=type(exc).__name__
        duration=(time.perf_counter()-started)*1000
        after=digest(encode({"summary":fixed["summary"],"findings":fixed["findings"]}))
        if before!=after:
            raise RuntimeError("Deterministic findings changed during model inference")
        measurements.append({"case_id":case["id"],"agent":case["agent"],
                             "status":status,"duration_ms":round(duration,2),
                             "fixed_findings_digest":before,"narrative":narrative,
                             "error_type":failure,"human_grounding_review":"PENDING"})
    durations=[x["duration_ms"] for x in measurements if x["status"]=="DRAFT_UNVERIFIED"]
    return {"schema":"HQ-LOCAL-MODEL-PROBE-0.1","model":model,
            "operator_attested_local_model":True,
            "cases_requested":len(cases),"responses":measurements,
            "model_errors":sum(x["status"]=="MODEL_ERROR" for x in measurements),
            "median_latency_ms":statistics.median(durations) if durations else None,
            "model_grounding_score":None,"human_review_required":True,
            "qualification_approved":False,
            "note":"Model responses require manual source-grounded review. Model pinning, network isolation and inference hardware must be independently verified."}

def main():
    p=argparse.ArgumentParser(description="Human-reviewed local Ollama model acceptance probe")
    p.add_argument("--enable-local-ollama",action="store_true")
    p.add_argument("--model",required=True)
    p.add_argument("--max-cases",type=int,default=30)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    result=probe(args.model,consent=args.enable_local_ollama,max_cases=args.max_cases)
    with Path(args.out).open("xb") as stream:
        stream.write(encode(result))
    print(json.dumps({"cases":result["cases_requested"],"model_errors":result["model_errors"],
                      "median_latency_ms":result["median_latency_ms"],
                      "human_grounding_review":"PENDING",
                      "qualification_approved":False},indent=2))
    raise SystemExit(1 if result["model_errors"] else 0)

if __name__=="__main__":
    main()
