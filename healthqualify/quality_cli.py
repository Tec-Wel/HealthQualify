"""Operator CLI for human-reviewed engineering records; no regulated approval.

Passwords requested interactively, never as argv. QMS handoff is a local
offline JSON package and does not transmit to any external quality system.
"""
from __future__ import annotations
import argparse
import getpass
import json
from pathlib import Path
from .assurance import encode
from .deviation_review import DeviationReview
from .release_qualification import ReleaseDecisions,release_plan
from .retention import RetentionStore

def main(argv=None):
    p=argparse.ArgumentParser(prog="healthqualify.quality_cli")
    p.add_argument("--db",default="healthqualify.db")
    subs=p.add_subparsers(dest="command",required=True)
    q=subs.add_parser("review-deviation")
    for name in ("username","deviation_id","disposition","rationale","evidence_ref"):
        q.add_argument(name)
    x=subs.add_parser("qms-export")
    x.add_argument("deviation_id")
    x.add_argument("--out",required=True)
    x=subs.add_parser("retain")
    x.add_argument("file")
    x.add_argument("kind",choices=("run","deviation_review","qms_handoff","release_review"))
    x.add_argument("--folder",required=True)
    x.add_argument("--days",type=int,default=365)
    x.add_argument("--legal-hold",action="store_true")
    x=subs.add_parser("retention-verify")
    x.add_argument("record_id")
    x.add_argument("--folder",required=True)
    x=subs.add_parser("release-plan")
    x.add_argument("protocol")
    x.add_argument("base_sha")
    x.add_argument("head_sha")
    x.add_argument("--out",required=True)
    x=subs.add_parser("release-review")
    x.add_argument("plan_file")
    x.add_argument("username")
    x.add_argument("decision",choices=("ACKNOWLEDGED","RETEST_REQUIRED","BLOCKED"))
    x.add_argument("rationale")
    args=p.parse_args(argv)
    if args.command=="review-deviation":
        store=DeviationReview(args.db)
        try:
            record=store.submit(args.username,getpass.getpass("QA password: "),
                args.deviation_id,args.disposition,args.rationale,args.evidence_ref)
        finally:store.close()
    elif args.command=="qms-export":
        store=DeviationReview(args.db)
        try: record=store.qms_export(args.deviation_id)
        finally:store.close()
        with Path(args.out).open("xb") as fd:
            fd.write(encode(record))
    elif args.command=="retain":
        store=RetentionStore(args.folder)
        try:record=store.add(Path(args.file).read_bytes(),args.kind,args.days,args.legal_hold)
        finally:store.close()
    elif args.command=="retention-verify":
        store=RetentionStore(args.folder)
        try:record={"verified":store.verify(args.record_id)}
        finally:store.close()
    elif args.command=="release-plan":
        protocol=json.loads(Path(args.protocol).read_text(encoding="utf-8"))
        record=release_plan(protocol,args.base_sha,args.head_sha)
        with Path(args.out).open("xb") as fd:
            fd.write(encode(record))
    elif args.command=="release-review":
        data=json.loads(Path(args.plan_file).read_text(encoding="utf-8"))
        if data.get("sha256")!=__import__("hashlib").sha256(encode(data["plan"])).hexdigest():
            raise ValueError("Release plan receipt digest mismatch")
        store=ReleaseDecisions(args.db)
        try:record=store.record(data["plan"],args.username,getpass.getpass("QA password: "),
                                args.decision,args.rationale)
        finally:store.close()
    else:raise ValueError("Unknown command")
    print(json.dumps(record,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
