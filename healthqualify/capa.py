"""Controlled deviation investigation and CAPA demonstrations.

A retest passing does not close a deviation by itself. Investigation, reviewer
and effectiveness assessment remain explicit human records. SQLite is not a
regulated protected audit log.
"""
from __future__ import annotations
import json
import sqlite3
import uuid
from datetime import datetime,timezone
from .workspace import Workspace

def utcnow():
    return datetime.now(timezone.utc).isoformat()

class CAPA:
    def __init__(self, database):
        self.work=Workspace(database)
        self.conn=self.work.conn
        with self.conn:
            self.conn.execute("""CREATE TABLE IF NOT EXISTS capa_cases(
              id TEXT PRIMARY KEY, deviation_id TEXT NOT NULL REFERENCES deviations(id),
              owner TEXT NOT NULL, risk TEXT NOT NULL,
              root_cause TEXT, corrective_action TEXT, effectiveness_criteria TEXT,
              status TEXT NOT NULL CHECK(status IN ('OPEN','INVESTIGATED','CLOSED')),
              reviewer TEXT, retest_run_id TEXT, opened_at TEXT NOT NULL, closed_at TEXT
            )""")

    def close(self):
        self.work.close()

    def open_case(self, deviation_id, owner, risk, actor):
        finding=self.work.one("deviations",deviation_id)
        if finding["status"]=="RESOLVED":
            raise ValueError("Cannot open CAPA for resolved deviation")
        if not isinstance(owner,str) or not owner.strip() or risk not in ("low","medium","high","critical") or not actor:
            raise ValueError("Owner, valid risk and actor required")
        ident=str(uuid.uuid4())
        with self.conn:
            self.conn.execute("""INSERT INTO capa_cases
                (id,deviation_id,owner,risk,status,opened_at) VALUES(?,?,?,?,'OPEN',?)""",
                (ident,deviation_id,owner,risk,utcnow()))
            self.work._audit(actor,"capa.opened",ident,{"deviation_id":deviation_id})
        return self.case(ident)

    def case(self, id):
        row=self.conn.execute("SELECT * FROM capa_cases WHERE id=?",(id,)).fetchone()
        if not row:
            raise KeyError("CAPA not found")
        return dict(row)

    def investigate(self, case_id, root_cause, action, effectiveness, actor):
        record=self.case(case_id)
        if record["status"]!="OPEN":
            raise ValueError("Investigation can only be recorded once")
        if not all(isinstance(x,str) and x.strip() for x in (root_cause,action,effectiveness,actor)):
            raise ValueError("Root cause, correction, effectiveness and actor required")
        with self.conn:
            self.conn.execute("""UPDATE capa_cases SET root_cause=?,corrective_action=?,
                effectiveness_criteria=?,status='INVESTIGATED' WHERE id=?""",
                (root_cause,action,effectiveness,case_id))
            self.work._audit(actor,"capa.investigated",case_id,{"recorded":True})
        return self.case(case_id)

    def close_case(self, case_id, reviewer, retest_run_id, effectiveness_evidence):
        record=self.case(case_id)
        if record["status"]!="INVESTIGATED":
            raise ValueError("Only investigated CAPA can close")
        if not isinstance(reviewer,str) or not reviewer.strip() or reviewer==record["owner"]:
            raise ValueError("Independent reviewer required")
        if not isinstance(effectiveness_evidence,str) or not effectiveness_evidence.strip():
            raise ValueError("Effectiveness evidence reference required")
        deviation=self.work.one("deviations",record["deviation_id"])
        if not deviation["test_id"]:
            raise ValueError("Unmapped requirement gap requires separate human disposition")
        original=self.work.one("runs",deviation["run_id"])
        rerun=self.work.one("runs",retest_run_id)
        if rerun["id"]==original["id"] or rerun["protocol_id"]!=original["protocol_id"]:
            raise ValueError("Retest must be a distinct run against the same protocol")
        tests=[t for t in rerun["results"]["results"] if t["id"]==deviation["test_id"]]
        if len(tests)!=1 or tests[0]["status"]!="PASS":
            raise ValueError("Linked retest has not passed")
        with self.conn:
            self.conn.execute("""UPDATE capa_cases SET status='CLOSED',reviewer=?,
                retest_run_id=?,closed_at=? WHERE id=?""",(reviewer,retest_run_id,utcnow(),case_id))
            self.work._audit(reviewer,"capa.closed",case_id,
                             {"retest_run_id":retest_run_id,"effectiveness_evidence_ref":effectiveness_evidence})
        return self.case(case_id)
