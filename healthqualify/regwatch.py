"""Regulatory source snapshots for human-reviewed change monitoring.

Works from supplied documents offline. It NEVER decides applicability or creates
an automatic regulatory requirement; fetch/update scheduling is out of scope.
"""
from __future__ import annotations
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from .regulatory import CATALOG, compare_text

class RegulationWatch:
    def __init__(self, database: str | Path):
        self.connection=sqlite3.connect(str(database))
        self.connection.row_factory=sqlite3.Row
        self.connection.execute("""CREATE TABLE IF NOT EXISTS regulatory_snapshots (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           framework TEXT NOT NULL, captured_at TEXT NOT NULL,
           source_url TEXT NOT NULL, sha256 TEXT NOT NULL, content TEXT NOT NULL)""")
        self.connection.commit()

    def close(self):
        self.connection.close()

    def capture(self, framework: str, supplied_text: str) -> dict:
        if framework not in CATALOG or not isinstance(supplied_text,str) or not supplied_text or len(supplied_text)>2_000_000:
            raise ValueError("Known framework and bounded supplied text required")
        recent=self.connection.execute(
            "SELECT * FROM regulatory_snapshots WHERE framework=? ORDER BY id DESC LIMIT 1",(framework,)).fetchone()
        sha=hashlib.sha256(supplied_text.encode()).hexdigest()
        if recent and recent["sha256"]==sha:
            return {"framework":framework,"changed":False,"snapshot_id":recent["id"],
                    "review_required":False,"note":"Byte-identical to latest stored snapshot"}
        with self.connection:
            cursor=self.connection.execute(
                "INSERT INTO regulatory_snapshots(framework,captured_at,source_url,sha256,content) VALUES(?,?,?,?,?)",
                (framework,datetime.now(timezone.utc).isoformat(),CATALOG[framework]["source"],sha,supplied_text))
        diff=compare_text(recent["content"],supplied_text) if recent else None
        return {"framework":framework,"changed":recent is not None,"snapshot_id":cursor.lastrowid,
                "sha256":sha,"diff":diff,"review_required":True,
                "source_claim":"Supplied by operator; not independently fetched or legally verified",
                "note":"Initial baseline" if recent is None else "Content changed; review applicability manually"}
