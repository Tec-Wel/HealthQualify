"""Reproducible, offline 30+ case evaluation for HealthQualify advisory agents.

The gold set is explicit human-authored labels for synthetic scenarios.
Scoring deterministic logic is NOT evidence that an LLM has been benchmarked.
"""
from __future__ import annotations
import copy
import json
from pathlib import Path
from .agents import investigate
from .protocol_v3 import validate_v3
from .assurance import digest,encode

ROOT=Path(__file__).resolve().parents[1]

def evaluate(cases_file=None, protocol_file=None):
    cases_file=Path(cases_file or ROOT/"evaluations"/"agent_cases.json")
    protocol_file=Path(protocol_file or ROOT/"examples"/"synthetic_lis_v3"/"protocol.json")
    protocol=json.loads(protocol_file.read_text(encoding="utf-8"))
    validate_v3(protocol)
    cases=json.loads(cases_file.read_text(encoding="utf-8"))
    if not isinstance(cases,list) or len(cases)<30 or len(cases)>500:
        raise ValueError("Expected at least 30 bounded independently labeled scenarios")
    seen=set()
    tp=fp=fn=0
    failures=[]
    by_agent={}
    for case in cases:
        if case["id"] in seen:
            raise ValueError("Duplicate evaluation case ID")
        seen.add(case["id"])
        p=copy.deepcopy(protocol)
        if case.get("add_uncovered_requirement"):
            req=copy.deepcopy(p["requirements"][0])
            req["id"]="URS-EVAL-"+case["id"]
            p["requirements"].append(req)
        registry={"systems":[{"id":"LIS","components":["healthqualify/healthcare.py"]}]}
        result=investigate(case["agent"],p,
                           changed_files=case.get("changed_files"),
                           registry=registry if case["agent"]=="dependency-investigator" else None)
        observed=set(x["code"] for x in result["findings"])
        expected=set(case["expected_codes"])
        hit=len(observed & expected)
        extra=len(observed-expected)
        missed=len(expected-observed)
        tp+=hit;fp+=extra;fn+=missed
        a=by_agent.setdefault(case["agent"],{"cases":0,"tp":0,"fp":0,"fn":0})
        a["cases"]+=1;a["tp"]+=hit;a["fp"]+=extra;a["fn"]+=missed
        if extra or missed or result["qualification_approved"] is not False:
            failures.append({"id":case["id"],"extra":sorted(observed-expected),
                             "missed":sorted(expected-observed)})
    precision=tp/(tp+fp) if tp+fp else None
    recall=tp/(tp+fn) if tp+fn else None
    return {"schema":"HQ-AGENT-EVAL-0.1","evaluation_cases":len(cases),
            "protocol_sha256":digest(protocol_file.read_bytes()),
            "labels_sha256":digest(cases_file.read_bytes()),
            "precision":precision,"recall":recall,
            "true_positive_labels":tp,"false_positive_labels":fp,
            "missed_labels":fn,"failures":failures,
            "by_agent":by_agent,"model_inference_tested":False,
            "model_accuracy":None,"clinical_validation":False,
            "qualification_approved":False,
            "note":"Only synthetic deterministic advisory logic was measured. Qwen inference, latency and model factuality require separate hardware validation."}

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--cases")
    p.add_argument("--protocol")
    p.add_argument("--out")
    a=p.parse_args()
    report=evaluate(a.cases,a.protocol)
    if a.out:
        target=Path(a.out)
        with target.open("xb") as stream:
            stream.write(encode(report))
    print(json.dumps(report,indent=2))
    raise SystemExit(0 if not report["failures"] else 1)

if __name__=="__main__":
    main()
