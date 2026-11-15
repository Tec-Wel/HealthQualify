"""Local append-only evidence registry with retention and hold metadata.

The files/SQLite database remain modifiable by privileged OS operators: this
is not WORM storage, regulated retention or an independent trusted audit log.
"""
from __future__ import annotations
import hashlib
import json
import os
import sqlite3
import uuid
from datetime import datetime,timezone,timedelta
from pathlib import Path

class RetentionStore:
    def __init__(self,folder):
        self.root=Path(folder)
        self.root.mkdir(parents=True,exist_ok=True,mode=0o700)
        if self.root.is_symlink():
            raise ValueError("Evidence root must not be a symlink")
        (self.root/"artifacts").mkdir(exist_ok=True,mode=0o700)
        self.db=sqlite3.connect(self.root/"registry.db")
        self.db.row_factory=sqlite3.Row
        self.db.execute("""CREATE TABLE IF NOT EXISTS records(
            id TEXT PRIMARY KEY, sha256 TEXT NOT NULL, source_kind TEXT NOT NULL,
            created_at TEXT NOT NULL, retain_until TEXT NOT NULL, legal_hold INTEGER NOT NULL,
            bytes INTEGER NOT NULL)""")
        self.db.commit()

    def close(self):self.db.close()

    def add(self,content,source_kind,retention_days=365,legal_hold=False):
        if not isinstance(content,bytes) or not content or len(content)>16*1024*1024:
            raise ValueError("Bounded nonempty technical evidence required")
        if source_kind not in {"run","deviation_review","qms_handoff","release_review"}:
            raise ValueError("Unsupported evidence type")
        if type(retention_days) is not int or not 1<=retention_days<=36500:
            raise ValueError("Retention interval out of bounds")
        if type(legal_hold) is not bool:
            raise ValueError("Explicit legal hold boolean required")
        uid=str(uuid.uuid4())
        at=datetime.now(timezone.utc)
        hashvalue=hashlib.sha256(content).hexdigest()
        destination=self.root/"artifacts"/(uid+".bin")
        with destination.open("xb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            with self.db:
                self.db.execute("INSERT INTO records VALUES(?,?,?,?,?,?,?)",
                    (uid,hashvalue,source_kind,at.isoformat(),
                     (at+timedelta(days=retention_days)).isoformat(),
                     1 if legal_hold else 0,len(content)))
        except Exception:
            destination.unlink(missing_ok=True)
            raise
        return {"id":uid,"sha256":hashvalue,"retention_until":(at+timedelta(days=retention_days)).isoformat(),
                "legal_hold":legal_hold,"technical_only":True}

    def verify(self,record_id):
        row=self.db.execute("SELECT * FROM records WHERE id=?",(record_id,)).fetchone()
        if not row:return False
        candidate=self.root/"artifacts"/(record_id+".bin")
        if candidate.is_symlink() or not candidate.is_file():return False
        data=candidate.read_bytes()
        return (len(data)==row["bytes"] and hashlib.sha256(data).hexdigest()==row["sha256"])

    def inventory(self):
        return [dict(r) for r in self.db.execute("SELECT * FROM records ORDER BY created_at,id")]
