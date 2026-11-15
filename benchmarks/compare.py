"""Repeatable equal-input synthetic benchmark of three execution strategies.

Real timing measurements on GitHub runners; no claims of clinical performance,
independent regulatory validation, or relative superiority beyond this fixture.
"""
from __future__ import annotations
import json
import os
import statistics
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from tempfile import TemporaryDirectory

from .independent_baseline import execute_baseline,traceability_baseline
from healthqualify.assurance import assess_v2,encode,digest

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/"examples"/"synthetic_lis_v2"/"protocol.json"

def _summary(results):
    return {state:sum(t["status"]==state for t in results)
            for state in ("PASS","FAIL","ERROR","NOT_RUN")}

def _pytest_once(protocol_path):
    with TemporaryDirectory() as tmp:
        report=Path(tmp)/"pytest.xml"
        env={**os.environ,"HQ_BENCH_PROTOCOL":str(protocol_path)}
        before=time.perf_counter()
        p=subprocess.run(
            [sys.executable,"-m","pytest","-q","--disable-warnings",
             "--junitxml",str(report),str(ROOT/"benchmarks"/"test_pytest_baseline.py")],
            cwd=ROOT,env=env,capture_output=True,text=True,timeout=45,
        )
        elapsed=(time.perf_counter()-before)*1000
        if p.returncode not in (0,1) or not report.is_file():
            raise RuntimeError("pytest harness failed: "+p.stderr[-1200:])
        suite=ET.parse(report).getroot().find(".//testsuite")
        if suite is None:
            raise RuntimeError("pytest JUnit XML missing suite")
        tests=int(suite.attrib["tests"])
        failures=int(suite.attrib.get("failures","0"))
        errors=int(suite.attrib.get("errors","0"))
        skipped=int(suite.attrib.get("skipped","0"))
        if tests!=7:
            raise RuntimeError("Unexpected pytest scenario count")
        return {"PASS":tests-failures-errors-skipped,"FAIL":failures,
                "ERROR":errors,"NOT_RUN":skipped},elapsed

def benchmark(path=PROTOCOL, repetitions=3, run_pytest=True):
    if type(repetitions) is not int or not 1<=repetitions<=10:
        raise ValueError("Repetitions must be 1..10")
    source=Path(path)
    doc=json.loads(source.read_text(encoding="utf-8"))
    if doc.get("system",{}).get("environment")!="synthetic":
        raise ValueError("Synthetic qualification protocol only")
    results={}
    for label in ("HealthQualify","Independent stdlib","Plain pytest"):
        if label=="Plain pytest" and not run_pytest:
            results[label]={"status":"NOT_RUN","reason":"pytest not installed"}
            continue
        durations=[]
        summary=None
        traceability_count=0
        for _ in range(repetitions):
            if label=="HealthQualify":
                start=time.perf_counter()
                report=assess_v2(doc)
                duration=(time.perf_counter()-start)*1000
                current=_summary(report["results"])
                traceability_count=len(report["traceability"])
            elif label=="Independent stdlib":
                start=time.perf_counter()
                observations=execute_baseline(doc)
                traces=traceability_baseline(doc,observations)
                duration=(time.perf_counter()-start)*1000
                current=_summary(observations)
                traceability_count=len(traces)
            else:
                current,duration=_pytest_once(source)
                traceability_count=0 # JUnit requires separate requirement mapping
            if summary is not None and current!=summary:
                raise RuntimeError("Nondeterministic test outcomes")
            summary=current
            durations.append(duration)
        results[label]={"status":"MEASURED","cases":sum(summary.values()),
                        "pass":summary["PASS"],"seeded_defects_detected":summary["FAIL"],
                        "error":summary["ERROR"],"not_run":summary["NOT_RUN"],
                        "requirement_links":traceability_count,
                        "median_runtime_ms":round(statistics.median(durations),3),
                        "runs":repetitions}
    return {"format":"HQ-SYNTH-BENCH-1",
            "input_sha256":digest(source.read_bytes()),"protocol":str(source),
            "known_seeded_defects":5,"expected_passes":2,
            "results":results,
            "setup_effort":"NOT_MEASURED",
            "maintenance_effort":"NOT_MEASURED",
            "interpretation":"Identical synthetic cases and fixtures; runtime includes pytest process startup only for pytest. Not a fair pure-engine performance comparison.",
            "claim_of_superiority":False,
            "qualification_approved":False}

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--protocol",default=str(PROTOCOL))
    p.add_argument("--repetitions",type=int,default=3)
    p.add_argument("--no-pytest",action="store_true")
    p.add_argument("--out")
    args=p.parse_args()
    result=benchmark(args.protocol,args.repetitions,not args.no_pytest)
    data=encode(result)
    if args.out:
        destination=Path(args.out)
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(data)
    print(json.dumps(result,indent=2))
    if any(x["status"]=="MEASURED" and
           (x["seeded_defects_detected"]!=5 or x["pass"]!=2 or x["cases"]!=7)
           for x in result["results"].values()):
        raise SystemExit(1)

if __name__=="__main__":
    main()
