"""Release event impact advisory. Never approves software for release.

For first tag or missing baseline, reports UNKNOWN_IMPACT and recommends every
declared test. Only immutable Git commit hashes are passed to the impact engine.
"""
from __future__ import annotations
import json
import os
import subprocess
from pathlib import Path
from .assurance import digest,encode
from .change_graph import plan_requalification
from .release_qualification import release_plan

def _git(*args):
    return subprocess.run(["git",*args],check=True,capture_output=True,
                          text=True,timeout=25).stdout.strip()

def advisory(protocol,tag):
    if not isinstance(tag,str) or not tag or len(tag)>120 or tag.startswith("-") or ".." in tag:
        raise ValueError("Invalid release tag")
    # Git arguments are fixed, shell=False, and tag name is resolved separately.
    head=_git("rev-list","-n","1","--end-of-options",f"refs/tags/{tag}")
    if not head:
        raise ValueError("Unknown release tag")
    try:
        parent_tag=_git("describe","--tags","--abbrev=0",f"{head}^")
        base=_git("rev-list","-n","1",f"refs/tags/{parent_tag}")
    except subprocess.CalledProcessError:
        base=None
    if base:
        return release_plan(protocol,base,head)
    all_tests=sorted(t["id"] for t in protocol["tests"])
    result={"schema":"HQ-RELEASE-IMPACT-1","base_sha":None,
            "head_sha":head,"protocol_digest":digest(encode(protocol)),
            "impact":{"impact":"UNKNOWN_IMPACT","reason":"No previous release tag",
                      "unmapped_paths":["<initial-release>"],
                      "recommended_test_ids":all_tests,
                      "human_review_required":True,"qualification_approved":False},
            "qualification_approved":False,"human_review_required":True}
    return {"plan":result,"sha256":digest(encode(result))}

def main():
    tag=os.environ.get("HQ_RELEASE_TAG","")
    protocol=json.loads(Path(os.environ.get("HQ_PROTOCOL",
        "examples/synthetic_lis_v3/protocol.json")).read_text())
    result=advisory(protocol,tag)
    outfile=Path(os.environ.get("HQ_RELEASE_OUTPUT","/tmp/hq-release-impact.json"))
    outfile.write_bytes(encode(result))
    summary=os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary,"a",encoding="utf-8") as stream:
            stream.write("### HealthQualify release impact (advisory only)\n\n")
            stream.write("- Release tag: `"+tag.replace("`","")+"\n")
            stream.write("- Impact: `"+result["plan"]["impact"]["impact"]+"`\n")
            stream.write("- Recommended tests: `"+", ".join(result["plan"]["impact"]["recommended_test_ids"])+"`\n")
            stream.write("- **Human review required. Qualification approval: NO.**\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
