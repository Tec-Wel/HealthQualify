"""Independent baseline for equal-input synthetic qualification benchmarking.

Uses only Python stdlib, does not import HealthQualify's test evaluator.
This is a limited generic testing baseline, not a replacement for full pytest
or any commercial validation package.
"""
from __future__ import annotations

def at_path(obj,field):
    current=obj
    for segment in field.split("."):
        if not segment or isinstance(current,list):
            raise ValueError("Unsupported JSON path")
        if not isinstance(current,dict) or segment not in current:
            raise KeyError(segment)
        current=current[segment]
    return current

def hl7_segment(text,name):
    for record in text.replace("\n","\r").split("\r"):
        fields=record.split("|")
        if fields[0]==name:
            return fields
    raise ValueError("Missing segment")

def baseline_observe(check,fixture,case):
    if check=="equals":
        return type(fixture) is type(case["expected"]) and fixture==case["expected"]
    if check=="present":
        return fixture is not None and fixture!=""
    if check=="role_denied":
        return isinstance(fixture,dict) and fixture.get("allowed") is False
    if check=="fhir_field_equals":
        actual=at_path(fixture,case["path"])
        return type(actual) is type(case["expected"]) and actual==case["expected"]
    if check=="hl7_field_equals":
        row=hl7_segment(fixture,case["segment"])
        index=case["field_index"]
        if index>=len(row):
            raise ValueError("HL7 field missing")
        return row[index]==case["expected"]
    raise ValueError("Unsupported test check")

def execute_baseline(protocol):
    results=[]
    for case in protocol["tests"]:
        fixture=protocol["fixtures"].get(case["fixture"])
        if case["fixture"] not in protocol["fixtures"]:
            status="NOT_RUN"
        else:
            try:
                status="PASS" if baseline_observe(case["check"],fixture,case) else "FAIL"
            except (ValueError,TypeError,KeyError,IndexError):
                status="ERROR"
        results.append({"id":case["id"],"status":status,
                        "requirement_ids":case["requirement_ids"]})
    return results

def traceability_baseline(protocol,results):
    rows=[]
    for req in protocol["requirements"]:
        matches=[x for x in results if req["id"] in x["requirement_ids"]]
        if not matches:
            status="UNCOVERED"
        else:
            status=next((state for state in ("FAIL","ERROR","NOT_RUN")
                         if any(x["status"]==state for x in matches)),"PASS")
        rows.append({"requirement_id":req["id"],"status":status,
                     "test_ids":[x["id"] for x in matches]})
    return rows
