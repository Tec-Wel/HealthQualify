"""SQLite consistent backup, restore verification and simple retention inventory.

Does not replace encrypted offsite backups, tested recovery plans or protected audit.
"""
from __future__ import annotations
import hashlib
import sqlite3
from pathlib import Path

def backup_sqlite(source, destination):
    src,dst=Path(source),Path(destination)
    if not src.is_file() or dst.exists() or src.resolve()==dst.resolve():
        raise ValueError("Source must exist and backup destination must be new")
    src_db=sqlite3.connect(str(src))
    dst_db=sqlite3.connect(str(dst))
    try:
        src_db.backup(dst_db)
        result=dst_db.execute("PRAGMA integrity_check").fetchone()[0]
        if result!="ok":
            raise ValueError("Backup integrity failed")
        dst_db.commit()
    finally:
        dst_db.close()
        src_db.close()
    digest=hashlib.sha256(dst.read_bytes()).hexdigest()
    return {"destination":str(dst),"sha256":digest,"integrity_check":"ok",
            "encrypted":False,"qualified_backup":False}

def verify_backup(path, trusted_sha256):
    source=Path(path)
    if not source.is_file() or len(trusted_sha256)!=64:
        return False
    if hashlib.sha256(source.read_bytes()).hexdigest()!=trusted_sha256:
        return False
    con=sqlite3.connect(f"file:{source.resolve()}?mode=ro",uri=True)
    try:
        return con.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
    finally:
        con.close()
