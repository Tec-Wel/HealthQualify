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
from .secure_api import serve_secure
from .security import IdentityStore
from .interop import check_local_fhir
from .fhir_secure import fetch_fhir, assert_fhir_field
from .dicom_device import inspect_dicom_file, inspect_equipment_snapshot
from .hl7_mllp import analyze_message
from .protected_export import protect_export, verify_export
from .attestations import attest_protocol
import base64
from .evidence import seal_export, verify_seal
from .regwatch import RegulationWatch

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
    cmd("bootstrap-admin","username")
    cmd("create-user","admin_username","username","role")
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
    approved=cmd("fhir-check-approved","url","field","expected_json")
    approved.add_argument("--authorize-read-only",action="store_true")
    dicom=cmd("dicom-synthetic","file")
    dicom.add_argument("--authorize-synthetic",action="store_true")
    h=cmd("hl7-mllp-inspect","file")
    h.add_argument("--authorize-synthetic",action="store_true")
    device=cmd("device-snapshot","file")
    device.add_argument("--authorize-synthetic",action="store_true")
    cmd("protect-export","source","destination")
    cmd("verify-protected","directory")
    cmd("review-attest","username","protocol_id","meaning","rationale")
    testfhir=cmd("fhir-check-local","url","path","expected_json")
    testfhir.add_argument("--allow-local-http",action="store_true")
    cmd("regwatch-capture","framework","text_file")
    cmd("seal","directory")
    cmd("verify-seal","directory")
    agent=cmd("draft-agent","role","model","text_file")
    agent.add_argument("--allow-local-ai",action="store_true")
    server=cmd("serve")
    server.add_argument("--port",type=int,default=8877)
    server.add_argument("--host",default="127.0.0.1")
    args=parser.parse_args(argv)
    store=None
    try:
        if args.command=="review-attest":
            import getpass
            password=getpass.getpass("Re-enter reviewer password: ")
            seed=base64.b64decode(os.environ.get("HEALTHQUALIFY_SIGN_SEED_B64",""),validate=True)
            data=attest_protocol(args.db,args.username,password,args.protocol_id,
                                 args.meaning,args.rationale,seed)
            print(json.dumps(data,indent=2))
            return 0
        if args.command=="fhir-check-approved":
            origin=os.environ.get("HEALTHQUALIFY_FHIR_ORIGIN","")
            token=os.environ.get("HEALTHQUALIFY_FHIR_BEARER","")
            data=fetch_fhir(args.url,approved_origin=origin,bearer_token=token,
                            consent=args.authorize_read_only)
            result=assert_fhir_field(data,args.field,json.loads(args.expected_json))
            print(json.dumps(result,indent=2))
            return 0 if result["status"]=="PASS" else 1
        if args.command=="dicom-synthetic":
            print(json.dumps(inspect_dicom_file(args.file,synthetic_only=args.authorize_synthetic),indent=2))
            return 0
        if args.command=="hl7-mllp-inspect":
            if not args.authorize_synthetic: raise ValueError("Synthetic-data authorization required")
            data=Path(args.file).read_bytes()
            print(json.dumps(analyze_message(data),indent=2))
            return 0
        if args.command=="device-snapshot":
            print(json.dumps(inspect_equipment_snapshot(read_json(args.file),
                authorized=args.authorize_synthetic),indent=2))
            return 0
        if args.command=="protect-export":
            key=base64.b64decode(os.environ.get("HEALTHQUALIFY_AES_KEY_B64",""),validate=True)
            seed=base64.b64decode(os.environ.get("HEALTHQUALIFY_SIGN_SEED_B64",""),validate=True)
            print(json.dumps(protect_export(Path(args.source),Path(args.destination),key,seed),indent=2))
            return 0
        if args.command=="verify-protected":
            public=base64.b64decode(os.environ.get("HEALTHQUALIFY_PUBLIC_KEY_B64",""),validate=True)
            ok=verify_export(Path(args.directory),public)
            print(json.dumps({"verified":ok}))
            return 0 if ok else 1
        if args.command=="fhir-check-local":
            expected=json.loads(args.expected_json)
            result=check_local_fhir(args.url,args.path,expected,authorized=args.allow_local_http)
            print(json.dumps(result,indent=2))
            return 0 if result["status"]=="PASS" else 1
        if args.command in {"seal","verify-seal"}:
            secret=os.getenv("HEALTHQUALIFY_EVIDENCE_KEY","").encode("utf-8")
            if args.command=="seal":
                print(json.dumps(seal_export(Path(args.directory),secret),indent=2))
                return 0
            ok=verify_seal(Path(args.directory),secret)
            print(json.dumps({"integrity_receipt_verified":ok}))
            return 0 if ok else 1
        if args.command=="regwatch-capture":
            watch=RegulationWatch(args.db)
            try:
                print(json.dumps(watch.capture(args.framework,Path(args.text_file).read_text(encoding="utf-8")),indent=2))
            finally:
                watch.close()
            return 0
        if args.command=="bootstrap-admin":
            import getpass
            password=getpass.getpass("Initial admin password (12+ characters): ")
            identity=IdentityStore(args.db)
            try:
                data=identity.bootstrap(args.username,password)
                print(json.dumps(data,indent=2))
            finally:
                identity.close()
            return 0
        if args.command=="create-user":
            import getpass
            admin_password=getpass.getpass("Admin password: ")
            password=getpass.getpass("New user password (12+ characters): ")
            identity=IdentityStore(args.db)
            try:
                token=identity.login(args.admin_username,admin_password)
                try:
                    actor=identity.authenticate(token)
                    data=identity.create_user(actor,args.username,password,args.role)
                finally:
                    identity.logout(token)
                print(json.dumps(data,indent=2))
            finally:
                identity.close()
            return 0
        if args.command=="serve":
            serve_secure(args.db,host=args.host,port=args.port)
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
