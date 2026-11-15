"""Internal benchmark fixture harness. Never assert superiority to third parties."""
from __future__ import annotations
import json
import time
from pathlib import Path
from .assurance import assess_v2

def run_internal_fixture(protocol_file):
    doc=json.loads(Path(protocol_file).read_text())
    start=time.perf_counter()
    result=assess_v2(doc)
    elapsed=(time.perf_counter()-start)*1000
    return {"label":"HealthQualify internal synthetic fixture",
            "checks":len(result["results"]),
            "failures":result["summary"]["FAIL"],
            "missing_or_error":result["summary"]["ERROR"]+result["summary"]["NOT_RUN"],
            "uncovered":sum(g["kind"]=="UNCOVERED" for g in result["gaps"]),
            "wall_ms":round(elapsed,3),
            "comparison_status":"NOT_RUN",
            "claim_of_competitor_superiority":False}
