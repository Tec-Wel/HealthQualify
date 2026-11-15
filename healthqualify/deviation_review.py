"""Controlled, exportable engineering deviation review for QMS hand-off.

Uses local IdentityStore for fresh-password QA authentication and explicit
system/run evidence binding. A signed technical record is NOT a Part 11
electronic signature, independent timestamp, or qualified QMS integration.
"""
from __future__ import annotations
import hashlib
import json
import uuid
from datetime import datetime,timezone
from .workspace import Workspace
from .security import IdentityStore, AuthenticationError
from .assurance import encode,digest

DISPOSITIONS={"ACCEPT_WITH_JUSTIFICATION","RETEST_REQUIRED","REJECTED"}

class DeviationReview:
    def __init__(self,db):
        self.work=Workspace(db)
        self.identity=IdentityStore(db)
        self.conn=self.work.conn
        with self.conn:
            self.conn.execute("""CREATE TABLE IF NOT EXISTS hq_deviation_review(
                id TEXT PRIMARY KEY, deviation_id TEXT NOT NULL REFERENCES deviations(id),
                reviewer TEXT NOT NULL, disposition TEXT NOT NULL,
                rationale TEXT NOT NULL, evidence_ref TEXT NOT NULL,
                original_run_digest TEXT NOT NULL, protocol_digest TEXT NOT NULL,
                created_at TEXT NOT NULL, record_digest TEXT NOT NULL)""")
            self.conn.execute("""CREATE INDEX IF NOT EXISTS hq_deviation_review_by_deviation
                ON hq_deviation_review(deviation_id)""")

    def close(self):
        self.identity.close()
        self.work.close()

    def submit(self,username,password,deviation_id,disposition,rationale,evidence_ref):
        if disposition not in DISPOSITIONS or not all(
                isinstance(x,str) and 4<=len(x.strip())<=2000
                for x in (rationale,evidence_ref)):
            raise ValueError("Review requires a permitted disposition and evidence/rationale")
        token=self.identity.login(username,password,duration=60)
        try:
            who=self.identity.authenticate(token)
            self.identity.authorize(who,"baseline")
            deviation=self.work.one("deviations",deviation_id)
            if deviation["status"]=="RESOLVED":
                raise ValueError("Cannot change resolved deviation")
            run=self.work.one("runs",deviation["run_id"])
            protocol=self.work.one("protocols",run["protocol_id"])
            if username==protocol["actor"]:
                raise AuthenticationError("Protocol author cannot review own deviation")
            if username in {deviation.get("disposition"),""}:
                raise AuthenticationError("Invalid reviewer")
            # Internal evidence refs have stable deterministic shape, never accept
            # free-form URLs or external raw data here.
            if not evidence_ref.startswith("hq-run:") or "/" not in evidence_ref[7:]:
                raise ValueError("An internal run/test evidence reference is required")
            valid_refs={t["evidence_ref"] for t in run["results"]["results"]}
            if evidence_ref not in valid_refs:
                raise ValueError("Evidence reference does not belong to original run")
            rid=str(uuid.uuid4())
            record={"id":rid,"deviation_id":deviation_id,"reviewer":username,
                    "disposition":disposition,"rationale":rationale.strip(),
                    "evidence_ref":evidence_ref,
                    "original_run_digest":run["result_digest"],
                    "protocol_digest":protocol["digest"],
                    "created_at":datetime.now(timezone.utc).isoformat(),
                    "qualification_approved":False}
            record_hash=digest(encode(record))
            with self.conn:
                self.conn.execute("""INSERT INTO hq_deviation_review
                    VALUES(?,?,?,?,?,?,?,?,?,?)""",
                    (rid,deviation_id,username,disposition,rationale.strip(),evidence_ref,
                     run["result_digest"],protocol["digest"],record["created_at"],record_hash))
                # A review is NOT a resolution; CAPA/retest closes it separately.
                self.conn.execute("""UPDATE deviations SET status='IN_REVIEW',updated_at=?
                    WHERE id=? AND status='OPEN'""",(record["created_at"],deviation_id))
                self.work._audit(username,"deviation.reviewed",deviation_id,
                    {"review_id":rid,"review_digest":record_hash,"disposition":disposition})
            return {"record":record,"sha256":record_hash}
        finally:
            self.identity.logout(token)

    def history(self,deviation_id):
        self.work.one("deviations",deviation_id)
        rows=self.conn.execute("""SELECT * FROM hq_deviation_review
            WHERE deviation_id=? ORDER BY created_at,id""",(deviation_id,)).fetchall()
        return [dict(r) for r in rows]

    def qms_export(self,deviation_id):
        """Return an offline vendor-neutral redacted hand-off; no network calls."""
        deviation=self.work.one("deviations",deviation_id)
        run=self.work.one("runs",deviation["run_id"])
        p=self.work.one("protocols",run["protocol_id"])
        reviews=self.history(deviation_id)
        for r in reviews:
            record={"id":r["id"],"deviation_id":r["deviation_id"],
                    "reviewer":r["reviewer"],"disposition":r["disposition"],
                    "rationale":r["rationale"],"evidence_ref":r["evidence_ref"],
                    "original_run_digest":r["original_run_digest"],
                    "protocol_digest":r["protocol_digest"],
                    "created_at":r["created_at"],"qualification_approved":False}
            if digest(encode(record))!=r["record_digest"]:
                raise ValueError("Review record integrity mismatch")
        if digest(encode(run["results"]))!=run["result_digest"]:
            raise ValueError("Stored run integrity mismatch")
        package={"format":"HQ-QMS-HANDOFF-1","deviation_id":deviation_id,
                 "status":deviation["status"],"test_id":deviation["test_id"],
                 "finding_kind":deviation["kind"],"run_id":run["id"],
                 "run_digest":run["result_digest"],"protocol_id":p["id"],
                 "protocol_digest":p["digest"],"review_records":reviews,
                 "qualification_approved":False,
                 "warning":"Offline technical QMS exchange only, not a validated QMS connector"}
        return {"package":package,"sha256":digest(encode(package))}
