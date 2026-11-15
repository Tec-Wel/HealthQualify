"""Controlled technical review attestation, not a Part 11 e-signature.

Requires fresh password verification, QA role, an immutable baseline digest,
an explicit meaning, and a cryptographic receipt. It does NOT establish legal
identity proofing, required signature manifestations, or validated e-signatures.
"""
from __future__ import annotations
import json
import sqlite3
from datetime import datetime, timezone
from .security import IdentityStore, AuthenticationError
from .workspace import Workspace
from .secure_vault import sign_manifest
from .assurance import encode, digest

MEANINGS={"REVIEWED","APPROVED_FOR_SYNTHETIC_EXECUTION","REJECTED"}

def attest_protocol(database: str, username: str, password: str, protocol_id: str,
                    meaning: str, rationale: str, private_seed: bytes) -> dict:
    if meaning not in MEANINGS or not isinstance(rationale,str) or not rationale.strip():
        raise ValueError("Explicit meaning and rationale required")
    ident=IdentityStore(database)
    work=Workspace(database)
    try:
        token=ident.login(username,password,duration=60)  # fresh password reauthentication
        try:
            principal=ident.authenticate(token)
            ident.authorize(principal,"baseline")
            protocol=work.one("protocols",protocol_id)
            if protocol["state"]!="BASELINED":
                raise ValueError("Protocol is not a baselined record")
            if protocol["actor"]==principal["username"]:
                raise AuthenticationError("Author cannot attest own protocol")
            data={"format":"HQ-REVIEW-1","protocol_id":protocol_id,"protocol_digest":protocol["digest"],
                  "signer":principal["username"],"meaning":meaning,
                  "rationale":rationale,"at":datetime.now(timezone.utc).isoformat()}
            receipt=sign_manifest(encode(data),private_seed)
            with work.conn:
                work.conn.execute("""CREATE TABLE IF NOT EXISTS hq_review_attestations(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    protocol_id TEXT NOT NULL, signer TEXT NOT NULL,
                    meaning TEXT NOT NULL, statement TEXT NOT NULL,
                    receipt TEXT NOT NULL, created_at TEXT NOT NULL)""")
                work.conn.execute("""INSERT INTO hq_review_attestations
                    (protocol_id,signer,meaning,statement,receipt,created_at)
                    VALUES(?,?,?,?,?,?)""",
                    (protocol_id,principal["username"],meaning,encode(data).decode(),
                     json.dumps(receipt,sort_keys=True),data["at"]))
                work._audit(principal["username"],"protocol.review_attested",protocol_id,
                            {"meaning":meaning,"protocol_digest":protocol["digest"]})
            return {"statement":data,"cryptographic_receipt":receipt,
                    "regulatory_esignature":False}
        finally:
            ident.logout(token)
    finally:
        ident.close()
        work.close()
