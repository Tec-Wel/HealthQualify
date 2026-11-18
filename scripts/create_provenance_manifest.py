"""Produce a reproducible local SHA-256 manifest; does NOT grant IP or release clearance.

Usage (run inside a reviewed clone):
  python scripts/create_provenance_manifest.py --output /tmp/healthqualify-provenance.json

The output inventories tracked website/doc graphics and dependency declarations.
Hashes prove byte identity, NOT authorship, license compatibility or freedom from secrets.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPHIC_SUFFIXES = {".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".woff", ".woff2", ".ttf", ".otf"}
DECLARATIONS = {"LICENSE", "NOTICE", "THIRD_PARTY_NOTICES.md", "website/package-lock.json",
                "website/package.json", "requirements-docs.txt", "requirements-security.txt"}
ASSET_PREFIXES = ("docs/assets/", "website/public/", "website/src/")


def tracked_paths() -> list[str]:
    output = subprocess.check_output(
        ["git", "-C", str(ROOT), "ls-files", "-z"], stderr=subprocess.PIPE
    )
    result = []
    for encoded in output.split(b"\0"):
        if not encoded:
            continue
        path = encoded.decode("utf-8", errors="surrogateescape")
        if path in DECLARATIONS or (path.startswith(ASSET_PREFIXES) and Path(path).suffix.lower() in GRAPHIC_SUFFIXES):
            result.append(path)
    return sorted(result)


def build_manifest() -> dict:
    records = []
    for rel in tracked_paths():
        file_path = ROOT / rel
        if not file_path.is_file() or file_path.is_symlink():
            raise RuntimeError(f"Tracked file missing or symbolic link: {rel}")
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
        records.append({"path": rel, "sha256": digest, "bytes": file_path.stat().st_size,
                        "category": "dependency-or-license-declaration" if rel in DECLARATIONS else "visual-asset"})
    commit = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
    ).strip()
    return {
        "schema": "healthqualify.provenance-inventory.v1",
        "repository_commit": commit,
        "scope": "tracked graphics/fonts in selected folders plus declared dependency/license files",
        "rights_verified": False,
        "legal_clearance": "NOT_GRANTED",
        "records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path,
                        help="Write JSON to an explicitly chosen location outside Git by preference.")
    args = parser.parse_args()
    result = build_manifest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {len(result['records'])} tracked provenance entries to {args.output}")
    print("SHA-256 is an identity fingerprint, not evidence of copyright ownership or regulatory clearance.")


if __name__ == "__main__":
    main()
