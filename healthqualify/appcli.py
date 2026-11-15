"""HealthQualify v0.3 workspace CLI; standard-library, offline by default."""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

from .workspace import Workspace
from .reports import export_run
from .regulatory import list_controls, applicability, compare_text
from .studio import draft_urs, risk_plan
from .ai import available_roles, local_draft
from .modelqual import score_classifier
from .api import serve

def read_json(file: str):
    return json.loads(Path(file).read_text(encoding="utf-8"))

def main(argv=None):
    parser=argparse.ArgumentParser(prog="healthqualify-workspace",
      description="Local development tool. No regulatory approval, clinical use or electronic signatures.")
    parser.add_argument("--db",default="healthqualify.db",help="SQLite workspace path")
    subs=parser.add_subparsers(dest="command",required=True)
    def cmd(name,*fields):
        p=subs.add_parser(name)
        for flag in fields:
            p.add_argument(flag)
        return p
    cmd("init")
    cmd("system-add","name","intended_use","owner")
    cmd("systems")
    cmd("protocol-add","system_id","path","actor")
    cmd("protocols")
    cmd("baseline","protocol_id","reviewer","rationale")
    cmd("run","protocol_id","actor")
    cmd("runs")
    cmd("deviations")
    cmd("audit")
    cmd("report","run_id","directory")
    cmd("frameworks")
    cmd("applicability","system_file","decisions_file")
    cmd("draft-urs","system_file","needs_file")
    cmd("risk-plan","system_file","frameworks_file","criticality")
    cmd("regulation-diff","before_file","after_file")
    cmd("modelqual","rows_file")
    cmd("agents")
    agent=cmd("draft-agent","role","model","text_file")
    agent.add_argument("--allow-local-ai",action="store_true")
    server=cmd("serve")
    server.add_argument("--port",type=int,default=8765)
    server.add_argument("--host",default="127.0.0.1")
    args=parser.parse_args(argv)
    store=None
    try:
        if args.command=="serve":
            serve(args.db,host=args.host,port=args.port,token=os.getenv("HEALTHQUALIFY_API_TOKEN"))
            return 0
        if args.command=="frameworks":data=list_controls()
        elif args.command=="applicability":data=applicability(read_json(args.system_file),read_json(args.decisions_file))
        elif args.command=="draft-urs":data=draft_urs(read_json(args.system_file),read_json(args.needs_file))
        elif args.command=="risk-plan":data=risk_plan(read_json(args.system_file),read_json(args.frameworks_file),args.criticality)
        elif args.command=="regulation-diff":
            data=compare_text(Path(args.before_file).read_text(),Path(args.after_file).read_text())
        elif args.command=="modelqual":data=score_classifier(read_json(args.rows_file))
        elif args.command=="agents":data=available_roles()
        elif args.command=="draft-agent":
            data=local_draft(args.role,Path(args.text_file).read_text(),args.model,consent=args.allow_local_ai)
        else:
            store=Workspace(args.db)
            if args.command=="init":data={"workspace":args.db,"initialized":True}
            elif args.command=="system-add":data=store.add_system(args.name,args.intended_use,args.owner)
            elif args.command=="systems":data=store.list("systems")
            elif args.command=="protocol-add":data=store.draft_protocol(args.system_id,read_json(args.path),args.actor)
            elif args.command=="protocols":data=store.list("protocols")
            elif args.command=="baseline":data=store.baseline(args.protocol_id,args.reviewer,args.rationale)
            elif args.command=="run":data=store.execute(args.protocol_id,args.actor)
            elif args.command=="runs":data=store.list("runs")
            elif args.command=="deviations":data=store.list("deviations")
            elif args.command=="audit":data=store.audit_events()
            elif args.command=="report":data=export_run(store,args.run_id,Path(args.directory))
            else:raise ValueError("Unknown command")
        print(json.dumps(data,indent=2,ensure_ascii=False))
        return 0
    except (OSError,KeyError,ValueError,TypeError,json.JSONDecodeError) as exc:
        print("HealthQualify:",str(exc),file=sys.stderr)
        return 2
    finally:
        if store is not None:store.close()

if __name__=="__main__":
    raise SystemExit(main())
