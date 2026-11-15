"""AES-GCM evidence encryption and Ed25519 artifact signatures.

This module provides cryptographic primitives, not an independently protected
regulated audit trail, validated time source, identity proofing, or 21 CFR Part 11
electronic signatures. Keys must be managed outside the evidence store.
"""
from __future__ import annotations
import base64
import json
import os
from pathlib import Path

def _cryptography():
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    except ImportError as exc:
        raise RuntimeError("Install cryptography for secure evidence operations") from exc
    return AESGCM,Ed25519PrivateKey,Ed25519PublicKey,Encoding,PublicFormat

def encrypt_evidence(plaintext: bytes, key: bytes, artifact_id: str) -> bytes:
    AESGCM,*_ = _cryptography()
    if not isinstance(plaintext,bytes) or len(plaintext)>16*1024*1024:
        raise ValueError("Artifact must be bounded bytes")
    if not isinstance(key,bytes) or len(key)!=32 or not artifact_id or len(artifact_id)>128:
        raise ValueError("32-byte key and artifact identifier required")
    nonce=os.urandom(12)
    ciphertext=AESGCM(key).encrypt(nonce,plaintext,artifact_id.encode())
    return json.dumps({"format":"HQ-AESGCM-1","artifact_id":artifact_id,
                       "nonce":base64.b64encode(nonce).decode(),
                       "ciphertext":base64.b64encode(ciphertext).decode()},
                      sort_keys=True).encode()

def decrypt_evidence(blob: bytes, key: bytes, artifact_id: str) -> bytes:
    AESGCM,*_ = _cryptography()
    if not isinstance(key,bytes) or len(key)!=32:
        raise ValueError("Invalid key length")
    obj=json.loads(blob)
    if obj.get("format")!="HQ-AESGCM-1" or obj.get("artifact_id")!=artifact_id:
        raise ValueError("Artifact binding mismatch")
    return AESGCM(key).decrypt(base64.b64decode(obj["nonce"]),
                               base64.b64decode(obj["ciphertext"]),artifact_id.encode())

def sign_manifest(manifest: bytes, private_seed: bytes) -> dict:
    _,Private,_,Encoding,PublicFormat=_cryptography()
    if not isinstance(private_seed,bytes) or len(private_seed)!=32:
        raise ValueError("Ed25519 seed must be 32 bytes")
    signer=Private.from_private_bytes(private_seed)
    signature=signer.sign(manifest)
    public=signer.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
    return {"format":"HQ-ED25519-1","signature":base64.b64encode(signature).decode(),
            "public_key":base64.b64encode(public).decode(),
            "warning":"Technical cryptographic signature, NOT a regulated electronic signature."}

def verify_manifest(manifest: bytes, receipt: dict, trusted_public_key: bytes) -> bool:
    _,_,Public,_,_=_cryptography()
    try:
        if receipt.get("format")!="HQ-ED25519-1" or len(trusted_public_key)!=32:
            return False
        if base64.b64decode(receipt["public_key"],validate=True)!=trusted_public_key:
            return False
        Public.from_public_bytes(trusted_public_key).verify(
            base64.b64decode(receipt["signature"],validate=True),manifest)
        return True
    except (ValueError,TypeError,KeyError):
        return False
    except Exception:
        return False
