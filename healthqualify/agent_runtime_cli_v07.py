"""Interactive, authenticated local CLI for the v0.7 contextual agent runtime.

No passwords or bearer tokens in shell arguments. No remote connections.
Use only an explicitly authorized synthetic local workspace.
"""
from __future__ import annotations
import argparse
import getpass
import json
import sys
from pathlib import Path
from .agent_runtime_v07 import ScopedAgentRuntime, EVENT_TYPES, REVIEW_STATES
from .agents import AGENTS
from .assurance import encode

def main(argv=None):
    p=argparse.ArgumentParser(description="HealthQualify v0.7 contextual agents (local engineering alpha)")
    p.add_argument("--db",default="healthqualify.db")
    p.add_argument("--user",required=True)
    sub=p.add_subparsers(dest="command",required=True)
    g=sub.add_parser("grant")
    g.add_argument("username");g.add_argument("system_id")
    x=sub.add_parser("revoke")
    x.add_argument("username");x.add_argument("system_id")
    context=sub.add_parser("context")
    context.add_argument("system_id")
    m=sub.add_parser("metrics")
    m.add_argument("system_id")
    q=sub.add_parser("review-queue")
    q.add_argument("system_id")
    a=sub.add_parser("analyze")
    a.add_argument("system_id");a.add_argument("agent",choices=AGENTS)
    a.add_argument("protocol")
    a.add_argument("--changed",nargs="*")
    a.add_argument("--registry")
    rv=sub.add_parser("review")
    rv.add_argument("observation_id")
    rv.add_argument("decision",choices=sorted(REVIEW_STATES))
    rv.add_argument("rationale")
    event=sub.add_parser("trigger")
    event.add_argument("system_id")
    event.add_argument("event_type",choices=sorted(EVENT_TYPES))
    event.add_argument("event_key")
    event.add_argument("source_reference")
    processing=sub.add_parser("process-trigger")
    processing.add_argument("trigger_id")
    processing.add_argument("protocol")
    processing.add_argument("--changed",nargs="*")
    args=p.parse_args(argv)
    runtime=ScopedAgentRuntime(args.db)
    try:
        token=runtime.identities.login(args.user,getpass.getpass("Local user password: "))
        try:
            if args.command=="grant":
                result=runtime.grant_system(token,args.username,args.system_id)
            elif args.command=="revoke":
                runtime.revoke_system(token,args.username,args.system_id)
                result={"revoked":True}
            elif args.command=="context":
                result=runtime.system_context(token,args.system_id)
            elif args.command=="metrics":
                result=runtime.metrics(token,args.system_id)
            elif args.command=="review-queue":
                result=runtime.review_queue(token,args.system_id)
            elif args.command=="analyze":
                protocol=json.loads(Path(args.protocol).read_text(encoding="utf-8"))
                registry=(json.loads(Path(args.registry).read_text(encoding="utf-8"))
                          if args.registry else None)
                result=runtime.analyze(token,args.system_id,protocol,args.agent,
                                       changed_files=args.changed,registry=registry)
            elif args.command=="review":
                result=runtime.review(token,args.observation_id,args.decision,args.rationale)
            elif args.command=="trigger":
                result=runtime.trigger(token,args.system_id,args.event_type,args.event_key,
                                       {"source_ref":args.source_reference})
            elif args.command=="process-trigger":
                protocol=json.loads(Path(args.protocol).read_text(encoding="utf-8"))
                result=runtime.process_trigger(token,args.trigger_id,protocol,
                                               changed_files=args.changed)
            else:
                raise ValueError("Unknown command")
            print(json.dumps(result,indent=2))
            return 0
        finally:
            runtime.identities.logout(token)
    except (PermissionError,ValueError,KeyError,OSError,json.JSONDecodeError) as e:
        print(type(e).__name__+": "+str(e),file=sys.stderr)
        return 2
    finally:
        runtime.close()

if __name__=="__main__":
    raise SystemExit(main())
