"""HealthQualify commands: legacy synthetic runner and v0.2 healthcare assurance."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from .assurance import save_v2, verify_v2, validate_v2
from .engine import save_run, verify_run
from .review import compare_protocols


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="healthqualify")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="execute v0.1 embedded synthetic fixtures")
    run.add_argument("protocol", type=Path)
    run.add_argument("--out", type=Path, required=True)
    check = commands.add_parser("verify", help="verify v0.1 evidence hashes")
    check.add_argument("run_dir", type=Path)

    run2 = commands.add_parser("run-v2", help="execute v0.2 synthetic healthcare qualification")
    run2.add_argument("protocol", type=Path)
    run2.add_argument("--out", type=Path, required=True)
    check2 = commands.add_parser("verify-v2", help="verify v0.2 evidence hashes")
    check2.add_argument("run_dir", type=Path)
    check2.add_argument("--trusted-manifest-sha256", help="SHA-256 saved separately from the evidence bundle")
    plan = commands.add_parser("validate-v2", help="validate v0.2 protocol without executing checks")
    plan.add_argument("protocol", type=Path)

    review = commands.add_parser("review-v2", help="identify protocol drift and conservative requalification scope")
    review.add_argument("before", type=Path)
    review.add_argument("after", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "review-v2":
            before = json.loads(args.before.read_text(encoding="utf-8"))
            after = json.loads(args.after.read_text(encoding="utf-8"))
            review_result = compare_protocols(before, after)
            print(json.dumps(review_result, indent=2))
            return 1 if review_result["human_review_required"] else 0
        if args.command == "verify":
            ok = verify_run(args.run_dir)
            print("Evidence hash check:", "MATCH" if ok else "MISMATCH")
            return 0 if ok else 1
        if args.command == "verify-v2":
            ok = verify_v2(args.run_dir, args.trusted_manifest_sha256)
            print("Evidence integrity check:", "MATCH" if ok else "MISMATCH")
            return 0 if ok else 1
        if args.command == "validate-v2":
            validate_v2(json.loads(args.protocol.read_text(encoding="utf-8")))
            print("Protocol schema: VALID (not approved)")
            return 0
        if args.command == "run-v2":
            result = save_v2(args.protocol.read_bytes(), args.out)
            print(json.dumps({"summary": result["summary"], "gap_count": len(result["gaps"]),
                              "qualification_approved": False}, indent=2))
            manifest_digest = hashlib.sha256((args.out / "manifest.json").read_bytes()).hexdigest()
            print("Evidence:", args.out)
            print("Manifest SHA-256 (store separately to establish trust):", manifest_digest)
            return 1 if result["gaps"] or any(r["status"] != "PASS" for r in result["traceability"]) else 0
        result = save_run(args.protocol.read_bytes(), args.out)
        print(json.dumps(result["summary"], indent=2))
        print(f"Evidence: {args.out}")
        return 0 if result["summary"]["FAIL"] == result["summary"]["ERROR"] == result["summary"]["NOT_RUN"] == 0 and all(
            r["status"] == "PASS" for r in result["traceability"]) else 1
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"HealthQualify error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
