"""Conservative release/tag qualification impact and human QA decision ledger.

No automatic release approval. Only source-path impact; unknown dependencies
cause full requalification recommendation. Intended for synthetic engineering
CI, not a regulated electronic signature.
"""
from __future__ import annotations
import json
import os
import re
import subprocess
from pathlib import Path
from .assurance import digest,encode
from .change_graph import plan_requalification
from .security import IdentityStore,AuthenticationError
from .workspace import Workspace

SHA=re.compile(r"^[a-f0-9]{40}$")

def release_plan(protocol,base_sha,head_sha,git="git"):
    if not all(isinstance(v,str) and SHA.fullmatch(v.lower()) for v in (base_sha,head_sha)):
        raise ValueError("Full trusted Git commit identifiers required")
    if base_sha==head_sha:
        raise ValueError("Release comparison requires distinct commits")
    result=subprocess.run([git,"diff","--name-only","--diff-filter=ACDMRT",
                          base_sha,head_sha,"--"],
                          capture_output=True,text=True,check=True,timeout=25)
    files=sorted(set(s.strip() for s in result.stdout.splitlines() if s.strip()))
    if not files:
        impact={"impact":"NO_CHANGED_FILES","changed_paths":[],
                "unmapped_paths":[],"recommended_test_ids":[],
                "human_review_required":True,"qualification_approved":False}
    else:
        impact=plan_requalification(protocol,files)
    plan={"schema":"HQ-RELEASE-IMPACT-1","base_sha":base_sha,"head_sha":head_sha,
          "protocol_digest":digest(encode(protocol)),"impact":impact,
          "qualification_approved":False,"human_review_required":True}
    return {"plan":plan,"sha256":digest(encode(plan))}

class ReleaseDecisions:
    def __init__(self,db):
        self.work=Workspace(db)
        self.identity=IdentityStore(db)
        self.conn=self.work.conn
        with self.conn:
            self.conn.execute("""CREATE TABLE IF NOT EXISTS hq_release_decisions(
                id INTEGER PRIMARY KEY AUTOINCREMENT, plan_digest TEXT NOT NULL,
                head_sha TEXT NOT NULL, reviewer TEXT NOT NULL, decision TEXT NOT NULL,
                rationale TEXT NOT NULL, created_at TEXT NOT NULL,
                decision_digest TEXT NOT NULL)""")
    def close(self):
        self.identity.close();self.work.close()
    def record(self,plan,username,password,decision,rationale):
        if not isinstance(plan,dict) or plan.get("schema")!="HQ-RELEASE-IMPACT-1":
            raise ValueError("Signed-off release plan input required")
        if not isinstance(rationale,str) or not 5<=len(rationale.strip())<=2000:
            raise ValueError("Review rationale required")
        if decision not in {"ACKNOWLEDGED","RETEST_REQUIRED","BLOCKED"}:
            raise ValueError("Only advisory release decisions supported")
        if not isinstance(plan.get("head_sha"),str) or not SHA.fullmatch(plan["head_sha"].lower()):
            raise ValueError("Unbound release head")
        if plan.get("qualification_approved") is not False or plan.get("human_review_required") is not True:
            raise ValueError("An approval claim is not permitted")
        token=self.identity.login(username,password,duration=60)
        try:
            actor=self.identity.authenticate(token);self.identity.authorize(actor,"baseline")
            from datetime import datetime,timezone
            event={"plan_digest":digest(encode(plan)),"head_sha":plan["head_sha"],
                   "reviewer":actor["username"],"decision":decision,
                   "rationale":rationale.strip(),
                   "created_at":datetime.now(timezone.utc).isoformat()}
            h=digest(encode(event))
            with self.conn:
                self.conn.execute("""INSERT INTO hq_release_decisions
                    (plan_digest,head_sha,reviewer,decision,rationale,created_at,decision_digest)
                    VALUES(?,?,?,?,?,?,?)""",
                    (*event.values(),h))
                self.work._audit(actor["username"],"release.impact_reviewed",plan["head_sha"],
                                 {"decision":decision,"plan_digest":event["plan_digest"]})
            return {"record":event,"sha256":h,"qualification_approved":False}
        finally:
            self.identity.logout(token)
