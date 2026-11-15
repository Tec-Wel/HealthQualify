"""v0.5 independent assurance, qualification evidence, impact and backup commands."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from .evidence_v3 import export_v3, verify_v3
from .change_graph import plan_requalification
from .assurance_profiles import plan
from .backup import backup_sqlite, verify_backup
from .benchmark import run_internal_fixture

def main(argv=None):
    root=argparse.ArgumentParser(description="HealthQualify v0.5 developer tools; no regulated approval")
    p=root.add_subparsers(dest="action",required=True)
    run=p.add_parser("run")
    run.add_argument("protocol")
    run.add_argument("--out",required=True)
    verify=p.add_parser("verify")
    verify.add_argument("directory")
    verify.add_argument("--trusted-manifest-sha256",required=True)
    impact=p.add_parser("impact")
    impact.add_argument("protocol")
    impact.add_argument("changed_files",nargs="+")
    profile=p.add_parser("profile")
    profile.add_argument("system")
    profile.add_argument("controls")
    profile.add_argument("--pathway",required=True,choices=("CSA","IQ-OQ-PQ"))
    backup=p.add_parser("backup")
    backup.add_argument("source")
    backup.add_argument("destination")
    backupcheck=p.add_parser("backup-verify")
    backupcheck.add_argument("path")
    backupcheck.add_argument("--trusted-sha256",required=True)
    bench=p.add_parser("benchmark")
    bench.add_argument("protocol")
    args=root.parse_args(argv)
    try:
        if args.action=="run":
            output=export_v3(Path(args.protocol).read_bytes(),Path(args.out))
            print(json.dumps(output,indent=2))
            return 1 if sum(output["summary"].get(x,0) for x in ("FAIL","ERROR","NOT_RUN")) else 0
        if args.action=="verify":
            ok=verify_v3(Path(args.directory),args.trusted_manifest_sha256)
            print(json.dumps({"verified":ok}))
            return 0 if ok else 1
        if args.action=="impact":
            result=plan_requalification(json.loads(Path(args.protocol).read_text()),args.changed_files)
        elif args.action=="profile":
            result=plan(json.loads(Path(args.system).read_text()),
                        json.loads(Path(args.controls).read_text()),args.pathway)
        elif args.action=="backup":
            result=backup_sqlite(args.source,args.destination)
        elif args.action=="backup-verify":
            ok=verify_backup(args.path,args.trusted_sha256)
            print(json.dumps({"verified":ok}))
            return 0 if ok else 1
        elif args.action=="benchmark":
            result=run_internal_fixture(args.protocol)
        else:
            raise ValueError("Unknown action")
        print(json.dumps(result,indent=2))
        return 0
    except (OSError,ValueError,TypeError,KeyError,json.JSONDecodeError) as exc:
        print("HealthQualify:",str(exc),file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
