"""Analyze changed repository paths in CI without ever approving a release.

The git diff is a *proposal*, not a validated dependency graph. Unknown
paths trigger UNKNOWN_IMPACT and rechecking every declared test.
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
from pathlib import Path
from .change_graph import plan_requalification

def analyze(base_sha: str, protocol_file: str):
    if not isinstance(base_sha,str) or len(base_sha)!=40 or any(x not in "0123456789abcdefABCDEF" for x in base_sha):
        raise ValueError("Valid 40-character base Git SHA required")
    diff=subprocess.run(
        ["git","diff","--name-only","--diff-filter=ACDMRT",f"{base_sha}...HEAD","--"],
        check=True,capture_output=True,text=True,timeout=20
    )
    files=sorted(set(line.strip() for line in diff.stdout.splitlines() if line.strip()))
    if not files:
        return {"impact":"NO_CHANGED_FILES","recommended_test_ids":[],
                "human_review_required":True,"qualification_approved":False}
    doc=json.loads(Path(protocol_file).read_text(encoding="utf-8"))
    return plan_requalification(doc,files)

def main():
    try:
        result=analyze(os.environ["HQ_BASE_SHA"],
                       os.getenv("HQ_PROTOCOL","examples/synthetic_lis_v3/protocol.json"))
        output=json.dumps(result,indent=2)
        print(output)
        summary=os.getenv("GITHUB_STEP_SUMMARY")
        if summary:
            with open(summary,"a",encoding="utf-8") as handle:
                handle.write("### HealthQualify: qualification impact (advisory)\n\n")
                handle.write("- Impact: `"+result["impact"]+"`\n")
                handle.write("- Human review required: **yes**\n")
                handle.write("- Qualification approved: **no**\n")
                handle.write("- Recommended test IDs: `"+", ".join(result["recommended_test_ids"])+"`\n\n")
        return 0
    except (ValueError,OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired,KeyError) as err:
        print("Impact analysis unavailable: "+str(err),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
