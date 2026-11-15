"""Offline CLI for HealthQualify's five advisory investigators."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .agents import AGENTS, investigate, load_protocol, load_registry


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Five read-only synthetic qualification agents; no regulated approval")
    parser.add_argument("agent", choices=AGENTS)
    parser.add_argument("protocol", help="Validated v0.3 synthetic protocol JSON")
    parser.add_argument("--changed", nargs="+", help="Explicit repository-relative changed files")
    parser.add_argument("--registry", help="Local dependency-registry JSON")
    parser.add_argument("--evidence-dir", help="Existing v0.3 evidence directory")
    parser.add_argument("--trusted-manifest-sha256",
                        help="Independently held trusted evidence manifest digest")
    parser.add_argument("--ollama", action="store_true",
                        help="Opt in to local Qwen explanation; defaults to no AI")
    parser.add_argument("--model", default="qwen3:8b")
    parser.add_argument("--out", help="Write a new draft report file; will not overwrite")
    args = parser.parse_args(argv)
    try:
        report = investigate(
            args.agent, load_protocol(args.protocol),
            changed_files=args.changed,
            registry=load_registry(args.registry) if args.registry else None,
            evidence_dir=args.evidence_dir,
            trusted_manifest_sha256=args.trusted_manifest_sha256,
            use_ollama=args.ollama, model=args.model)
        encoded = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        if args.out:
            with Path(args.out).open("x", encoding="utf-8") as target:
                target.write(encoded)
        print(encoded, end="")
        return 0
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as err:
        print("HealthQualify agent: " + str(err), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
