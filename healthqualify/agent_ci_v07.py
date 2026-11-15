"""GitHub main-push advisory: run all five deterministic agents on actual code diff.

This CI job uses only synthetic local fixtures and never accesses customer
workspaces, patient data, secrets, or external model providers. It is NOT an
organization's regulated release/quality gate.
"""
from __future__ import annotations
import json
import os
import subprocess
import tempfile
from pathlib import Path
from .agent_orchestrator import AgentHistory
from .assurance import encode

def changed_files():
    diff=subprocess.run(["git","diff","--name-only","--diff-filter=ACDMRT",
                         "HEAD^","HEAD","--"],capture_output=True,text=True,
                        check=True,timeout=20)
    paths=sorted(set(line.strip() for line in diff.stdout.splitlines() if line.strip()))
    if len(paths)>500:
        raise ValueError("Too many files for bounded CI advisory")
    return paths

def run_ci():
    paths=changed_files()
    if not paths:
        return {"state":"NO_CHANGES","jobs":[],"qualification_approved":False}
    with tempfile.TemporaryDirectory() as folder:
        history=AgentHistory(Path(folder)/"agent-ci.db")
        try:
            results=history.run_all(
                "github_actions", "examples/synthetic_lis_v3/protocol.json",
                changed_files=paths,registry_path="examples/agents/dependencies.json")
            jobs=[{"agent":item["agent"],"state":item["state"],
                   "report":item["report"]} for item in results["jobs"]]
            if any(j["state"]!="DRAFT" or j["report"]["qualification_approved"] is not False
                   for j in jobs):
                failures=[{"agent":j["agent"],"state":j["state"],"error":j.get("error")}
                          for j in results["jobs"] if j["state"]!="DRAFT" or
                          not j.get("report") or j["report"].get("qualification_approved") is not False]
                raise RuntimeError("Agent investigation did not produce safe drafts: "+repr(failures))
            return {"state":"DRAFT_ONLY","changed_files":paths,"jobs":jobs,
                    "qualification_approved":False,"human_review_required":True}
        finally:
            history.close()

def main():
    report=run_ci()
    target=Path(os.getenv("HQ_AGENT_ADVISORY_OUT","agent-main-advisories.json"))
    with target.open("xb") as stream:stream.write(encode(report))
    summary=os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary,"a",encoding="utf-8") as f:
            f.write("### HealthQualify Five-Agent Advisory (synthetic CI)\n\n")
            f.write("State: **"+report["state"]+"**. Human review required; qualification approved: **NO**.\n\n")
            for row in report["jobs"]:
                f.write("- "+row["agent"]+": "+row["state"]+
                        " ("+str(len(row["report"]["findings"]))+" findings)\n")
    print(json.dumps({"state":report["state"],"changed_files":len(report.get("changed_files",[])),
                      "agents":len(report["jobs"]),"qualification_approved":False},indent=2))

if __name__=="__main__":
    main()
