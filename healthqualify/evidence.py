"""Optional HMAC integrity receipts for technical exports.

HMAC receipts are NOT Part 11 electronic signatures, trusted timestamps, or
independent proof of who performed a regulated activity.
"""
from __future__ import annotations
import hashlib
import hmac
import json
from pathlib import Path

def seal_export(directory: Path, secret: bytes) -> dict:
    if not isinstance(secret,bytes) or len(secret)<32:
        raise ValueError("A 32+ byte secret from outside the export directory is required")
    data=(directory/"manifest.json").read_bytes()
    receipt={"method":"HMAC-SHA256","manifest_sha256":hashlib.sha256(data).hexdigest(),
             "mac":hmac.new(secret,data,hashlib.sha256).hexdigest(),
             "warning":"Shared-secret integrity receipt; not a regulated electronic signature."}
    path=directory/"receipt.json"
    with path.open("x",encoding="utf-8") as stream:
        json.dump(receipt,stream,sort_keys=True)
    return receipt

def verify_seal(directory: Path, secret: bytes) -> bool:
    try:
        if not isinstance(secret,bytes) or len(secret)<32:
            return False
        manifest=(directory/"manifest.json").read_bytes()
        receipt=json.loads((directory/"receipt.json").read_text(encoding="utf-8"))
        if receipt.get("method")!="HMAC-SHA256":
            return False
        return (hmac.compare_digest(receipt.get("manifest_sha256",""),hashlib.sha256(manifest).hexdigest())
                and hmac.compare_digest(receipt.get("mac",""),
                                        hmac.new(secret,manifest,hashlib.sha256).hexdigest()))
    except (OSError,ValueError,TypeError):
        return False
