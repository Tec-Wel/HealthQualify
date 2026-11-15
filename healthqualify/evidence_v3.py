"""Verifiable v0.3 technical execution receipts with protocol and runner provenance.

A user-held manifest digest is a trust anchor; without one this proves only
internal file consistency. It is not tamper-proof regulated record storage.
"""
from __future__ import annotations
import json
from pathlib import Path
from .assurance import digest, encode
from .protocol_v3 import execute_v3, validate_v3

ARTIFACTS = ("protocol.json","results.json")

def export_v3(protocol_bytes: bytes, path: Path):
    if not isinstance(protocol_bytes, bytes) or len(protocol_bytes)>1024*1024:
        raise ValueError("Bounded protocol bytes required")
    doc=json.loads(protocol_bytes)
    validate_v3(doc)
    result=execute_v3(doc)
    files={"protocol.json":protocol_bytes,"results.json":encode(result)}
    path.mkdir(parents=True,exist_ok=False)
    try:
        for name,value in files.items():
            (path/name).write_bytes(value)
        manifest={"schema":"HQ-EVIDENCE-0.3",
                  "source_protocol_sha256":digest(protocol_bytes),
                  "canonical_protocol_sha256":digest(encode(doc)),
                  "build_sha":doc["system"]["build_sha"],
                  "runner_version":doc["execution_policy"]["runner_version"],
                  "environment":doc["system"]["environment"],
                  "generated_at":result["executed_at_utc"],
                  "files":{n:digest(v) for n,v in files.items()},
                  "qualification_approved":False}
        (path/"manifest.json").write_bytes(encode(manifest))
        return {"summary":result["summary"],"manifest_sha256":digest(encode(manifest)),
                "qualification_approved":False}
    except Exception:
        # Do not return a successful execution receipt after a partial write.
        raise

def verify_v3(path: Path, trusted_manifest_sha256: str):
    if not isinstance(trusted_manifest_sha256,str) or len(trusted_manifest_sha256)!=64:
        return False
    try:
        raw=(path/"manifest.json").read_bytes()
        if digest(raw)!=trusted_manifest_sha256:
            return False
        manifest=json.loads(raw)
        if manifest.get("schema")!="HQ-EVIDENCE-0.3" or manifest.get("qualification_approved") is not False:
            return False
        files=manifest.get("files")
        if not isinstance(files,dict) or set(files)!=set(ARTIFACTS):
            return False
        for name in ARTIFACTS:
            if not (path/name).is_file() or digest((path/name).read_bytes())!=files[name]:
                return False
        protocol_bytes=(path/"protocol.json").read_bytes()
        doc=json.loads(protocol_bytes)
        validate_v3(doc)
        results=json.loads((path/"results.json").read_bytes())
        return (manifest["source_protocol_sha256"]==digest(protocol_bytes)
                and manifest["canonical_protocol_sha256"]==digest(encode(doc))
                and manifest["build_sha"]==doc["system"]["build_sha"]
                and manifest["runner_version"]==doc["execution_policy"]["runner_version"]
                and results.get("build_sha")==manifest["build_sha"]
                and results.get("runner_version")==manifest["runner_version"]
                and results.get("qualification_approved") is False
                and results.get("protocol_sha256")==manifest["canonical_protocol_sha256"])
    except (OSError,ValueError,TypeError,KeyError,UnicodeDecodeError):
        return False
