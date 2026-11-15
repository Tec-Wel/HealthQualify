"""Encrypted, signed technical evidence archives with external keys.

Encrypted artifacts and signed manifest are suitable for engineering integrity
checks only; not regulated record immutability or legally binding e-signatures.
"""
from __future__ import annotations
import base64
import hashlib
import json
from pathlib import Path
from .secure_vault import encrypt_evidence, decrypt_evidence, sign_manifest, verify_manifest

ARTIFACTS=("report.html","run.json","deviations.json","manifest.json")

def protect_export(source: Path, destination: Path, encryption_key: bytes, signing_seed: bytes):
    if destination.exists():
        raise FileExistsError("Protected evidence directory already exists")
    if not source.is_dir() or source.resolve()==destination.resolve():
        raise ValueError("Source and target directories must differ")
    payloads={}
    for name in ARTIFACTS:
        raw=(source/name).read_bytes()
        if len(raw)>16*1024*1024: raise ValueError("Artifact too large")
        payloads[name]=raw
    destination.mkdir(parents=True,exist_ok=False,mode=0o700)
    hashes={}
    for name,raw in payloads.items():
        encrypted=encrypt_evidence(raw,encryption_key,name)
        (destination/(name+".enc")).write_bytes(encrypted)
        hashes[name+".enc"]=hashlib.sha256(encrypted).hexdigest()
    manifest=json.dumps({"format":"HQ-PROTECTED-1","files":hashes,"encrypted":True,
                         "warning":"Technical records only; no regulated e-signature."},
                        sort_keys=True,separators=(",",":")).encode()
    (destination/"vault-manifest.json").write_bytes(manifest)
    receipt=sign_manifest(manifest,signing_seed)
    (destination/"vault-signature.json").write_text(json.dumps(receipt,sort_keys=True),encoding="utf-8")
    return {"files":len(hashes),"signature":receipt,"warning":"Not Part 11 electronic signatures"}

def verify_export(directory: Path, public_key: bytes) -> bool:
    try:
        manifest=(directory/"vault-manifest.json").read_bytes()
        receipt=json.loads((directory/"vault-signature.json").read_text())
        if not verify_manifest(manifest,receipt,public_key):
            return False
        doc=json.loads(manifest)
        hashes=doc.get("files")
        if doc.get("format")!="HQ-PROTECTED-1" or set(hashes or {})!=set(n+".enc" for n in ARTIFACTS):
            return False
        return all(hashlib.sha256((directory/name).read_bytes()).hexdigest()==digest
                   for name,digest in hashes.items())
    except (OSError,ValueError,TypeError,KeyError):
        return False
