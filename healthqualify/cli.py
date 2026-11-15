"""Run with python -m healthqualify.cli."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .engine import save_run, verify_run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="healthqualify")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="execute embedded synthetic qualification fixtures")
    run.add_argument("protocol", type=Path)
    run.add_argument("--out", type=Path, required=True)
    check = commands.add_parser("verify", help="verify hashes against local manifest")
    check.add_argument("run_dir", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "verify":
            ok = verify_run(args.run_dir)
            print("Evidence hash check:", "MATCH" if ok else "MISMATCH")
            return 0 if ok else 1
        result = save_run(args.protocol.read_bytes(), args.out)
        print(json.dumps(result["summary"], indent=2))
        print(f"Evidence: {args.out}")
        return 0 if result["summary"]["FAIL"] == result["summary"]["ERROR"] == result["summary"]["NOT_RUN"] == 0 and all(
            r["status"] == "PASS" for r in result["traceability"]) else 1
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"HealthQualify error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
