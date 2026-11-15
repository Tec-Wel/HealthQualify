"""SQLite-backed development workspace for qualification lifecycle records.

This is deliberately NOT a validated electronic records/signatures implementation.
Workspace access control is provided by the application API, not by SQLite itself.
"""
from __future__ import annotations
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .assurance import encode, digest, assess_v2, validate_v2
from .privacy import minimize_result

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def key() -> str:
    return str(uuid.uuid4())

class Workspace:
    def __init__(self, database: str | Path):
        self.database = str(database)
        self.conn = sqlite3.connect(self.database)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("PRAGMA busy_timeout=3000")
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS systems(
          id TEXT PRIMARY KEY, name TEXT NOT NULL, intended_use TEXT NOT NULL,
          owner TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS protocols(
          id TEXT PRIMARY KEY, system_id TEXT NOT NULL REFERENCES systems(id),
          version INTEGER NOT NULL, state TEXT NOT NULL CHECK(state IN ('DRAFT','BASELINED')),
          payload TEXT NOT NULL, digest TEXT NOT NULL, actor TEXT NOT NULL, created_at TEXT NOT NULL,
          UNIQUE(system_id,version));
        CREATE TABLE IF NOT EXISTS runs(
          id TEXT PRIMARY KEY, protocol_id TEXT NOT NULL REFERENCES protocols(id),
          results TEXT NOT NULL, result_digest TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS deviations(
          id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id),
          test_id TEXT, kind TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('OPEN','IN_REVIEW','RESOLVED')),
          disposition TEXT, retest_run_id TEXT REFERENCES runs(id), updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS audit(
          id INTEGER PRIMARY KEY AUTOINCREMENT, occurred_at TEXT NOT NULL,
          actor TEXT NOT NULL, action TEXT NOT NULL, object_id TEXT NOT NULL, detail TEXT NOT NULL);
        """)
        self.conn.commit()

    def close(self):
        self.conn.close()

    def _audit(self, actor: str, action: str, obj: str, detail: Any):
        self.conn.execute("INSERT INTO audit(occurred_at,actor,action,object_id,detail) VALUES(?,?,?,?,?)",
                          (now(),actor,action,obj,json.dumps(detail,sort_keys=True)))

    def add_system(self, name: str, intended_use: str, owner: str) -> dict:
        if not all(isinstance(x,str) and x.strip() and len(x)<=512 for x in (name,intended_use,owner)):
            raise ValueError("Name, intended use and owner are required")
        ident=key()
        with self.conn:
            self.conn.execute("INSERT INTO systems VALUES(?,?,?,?,?)",(ident,name,intended_use,owner,now()))
            self._audit(owner,"system.created",ident,{"name":name})
        return self.one("systems",ident)

    def one(self, table: str, ident: str) -> dict:
        if table not in {"systems","protocols","runs","deviations"}:
            raise ValueError("Invalid table")
        row=self.conn.execute(f"SELECT * FROM {table} WHERE id=?",(ident,)).fetchone()
        if row is None:
            raise KeyError(f"{table} record not found")
        data=dict(row)
        if table=="protocols":
            data["payload"]=json.loads(data["payload"])
        if table=="runs":
            data["results"]=json.loads(data["results"])
        return data

    def list(self, table: str, limit: int = 100) -> list[dict]:
        if table not in {"systems","protocols","runs","deviations"}:
            raise ValueError("Invalid table")
        if type(limit) is not int or not 1<=limit<=100:
            raise ValueError("Invalid limit")
        return [self.one(table,row["id"]) for row in self.conn.execute(
            f"SELECT id FROM {table} ORDER BY rowid DESC LIMIT ?",(limit,)).fetchall()]

    def draft_protocol(self, system_id: str, payload: dict, actor: str) -> dict:
        validate_v2(payload)
        if payload["system"]["id"] != system_id:
            raise ValueError("Protocol system id must match workspace system id")
        if not actor or not isinstance(actor,str):
            raise ValueError("Actor required")
        self.one("systems",system_id)
        value=encode(payload).decode()
        with self.conn:
            version=self.conn.execute("SELECT COALESCE(MAX(version),0)+1 FROM protocols WHERE system_id=?",
                                      (system_id,)).fetchone()[0]
            ident=key()
            self.conn.execute("INSERT INTO protocols VALUES(?,?,?,?,?,?,?,?)",
                (ident,system_id,version,"DRAFT",value,digest(value.encode()),actor,now()))
            self._audit(actor,"protocol.drafted",ident,{"version":version})
        return self.one("protocols",ident)

    def baseline(self, protocol_id: str, reviewer: str, note: str) -> dict:
        """Internal demo baseline record. Not a legally binding e-signature."""
        if not reviewer or not reviewer.strip() or not note or not note.strip():
            raise ValueError("Reviewer and review rationale required")
        record=self.one("protocols",protocol_id)
        if record["state"] != "DRAFT":
            raise ValueError("A baseline cannot be reapproved in place")
        if record["actor"] == reviewer:
            raise ValueError("Reviewer must differ from protocol author")
        with self.conn:
            self.conn.execute("UPDATE protocols SET state='BASELINED' WHERE id=? AND state='DRAFT'",(protocol_id,))
            self._audit(reviewer,"protocol.baselined",protocol_id,{"note":note,"digest":record["digest"]})
        return self.one("protocols",protocol_id)

    def execute(self, protocol_id: str, actor: str, allow_draft: bool = False) -> dict:
        protocol=self.one("protocols",protocol_id)
        if protocol["state"]!="BASELINED" and not allow_draft:
            raise ValueError("Draft execution requires explicit allow_draft")
        if not actor:
            raise ValueError("Actor required")
        if digest(encode(protocol["payload"])) != protocol["digest"]:
            raise ValueError("Protocol digest mismatch")
        result=minimize_result(assess_v2(protocol["payload"]))
        rid=key()
        encoded=encode(result).decode()
        with self.conn:
            self.conn.execute("INSERT INTO runs VALUES(?,?,?,?,?)",
                              (rid,protocol_id,encoded,digest(encoded.encode()),now()))
            for finding in result["gaps"]:
                self.conn.execute("INSERT INTO deviations VALUES(?,?,?,?,?,?,?,?)",
                     (key(),rid,finding.get("test_id"),finding["kind"],"OPEN",None,None,now()))
            self._audit(actor,"run.executed",rid,{"protocol_id":protocol_id,"summary":result["summary"],
                                                "draft_execution": protocol["state"]!="BASELINED"})
        return self.one("runs",rid)

    def disposition(self, deviation_id: str, reviewer: str, rationale: str,
                    retest_run_id: str | None = None) -> dict:
        if not reviewer or not rationale or not rationale.strip():
            raise ValueError("Reviewer and rationale required")
        entry=self.one("deviations",deviation_id)
        if entry["status"]=="RESOLVED":
            raise ValueError("Closed deviations cannot be altered")
        if not retest_run_id:
            raise ValueError("Evidence-linked retest is required")
        rerun=self.one("runs",retest_run_id)
        original=self.one("runs",entry["run_id"])
        if rerun["id"] == original["id"] or rerun["protocol_id"] != original["protocol_id"]:
            raise ValueError("Retest must be a distinct run against the same protocol")
        target=[x for x in rerun["results"]["results"] if x["id"]==entry["test_id"]]
        if len(target)!=1 or target[0]["status"]!="PASS":
            raise ValueError("Retest did not pass or lacks target test; cannot close")
        with self.conn:
            self.conn.execute("UPDATE deviations SET status='RESOLVED', disposition=?, retest_run_id=?, updated_at=? WHERE id=?",
                              (rationale,retest_run_id,now(),deviation_id))
            self._audit(reviewer,"deviation.resolved",deviation_id,{"retest_run_id":retest_run_id,"rationale":rationale})
        return self.one("deviations",deviation_id)

    def audit_events(self, limit: int = 100) -> list[dict]:
        if type(limit) is not int or not 1<=limit<=100:
            raise ValueError("Invalid limit")
        return [dict(row) for row in self.conn.execute("SELECT * FROM audit ORDER BY id DESC LIMIT ?",(limit,))]
