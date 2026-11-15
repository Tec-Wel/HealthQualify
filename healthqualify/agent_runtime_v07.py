"""HealthQualify v0.7: scoped, read-only, history-aware agent runtime.

The existing five deterministic investigators remain authoritative. This local
developer runtime binds their advisory findings to SQLite qualification records,
requires authenticated users and explicit per-system grants, records bounded
trigger events, and supports human *draft-review* decisions. It does not
perform clinical actions, alter tests, close CAPAs or authorize a release.
"""
from __future__ import annotations
import hashlib
import json
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .agents import AGENTS, investigate
from .assurance import encode, digest
from .protocol_v3 import validate_v3
from .security import AuthenticationError, IdentityStore
from .workspace import Workspace

EVENT_TYPES = {"RELEASE_CHANGED", "QUALIFICATION_FAILED", "COVERAGE_GAP"}
REVIEW_STATES = {"ACKNOWLEDGED", "NEEDS_INVESTIGATION", "DISMISSED"}
READ_LIMIT = 50


def _utc():
    return datetime.now(timezone.utc).isoformat()


class ScopedAgentRuntime:
    """Single-site development DB. No tenant isolation or regulatory e-signature."""
    def __init__(self, database):
        self.workspace = Workspace(database)
        self.identities = IdentityStore(str(database))
        self.conn = self.workspace.conn
        self.conn.executescript("""
          CREATE TABLE IF NOT EXISTS agent_system_grants(
            username TEXT NOT NULL, system_id TEXT NOT NULL REFERENCES systems(id),
            PRIMARY KEY(username,system_id));
          CREATE TABLE IF NOT EXISTS agent_observations(
            id TEXT PRIMARY KEY, system_id TEXT NOT NULL REFERENCES systems(id),
            actor TEXT NOT NULL, agent TEXT NOT NULL, status TEXT NOT NULL,
            protocol_digest TEXT NOT NULL, created_at TEXT NOT NULL,
            elapsed_ms REAL NOT NULL, model TEXT NOT NULL, report TEXT NOT NULL,
            report_digest TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS agent_review_queue(
            observation_id TEXT PRIMARY KEY REFERENCES agent_observations(id),
            disposition TEXT NOT NULL DEFAULT 'PENDING',
            reviewer TEXT, rationale TEXT, reviewed_at TEXT);
          CREATE TABLE IF NOT EXISTS agent_triggers(
            id TEXT PRIMARY KEY, system_id TEXT NOT NULL REFERENCES systems(id),
            event_type TEXT NOT NULL, event_key TEXT NOT NULL,
            payload_digest TEXT NOT NULL, actor TEXT NOT NULL,
            state TEXT NOT NULL, created_at TEXT NOT NULL,
            UNIQUE(system_id,event_type,event_key));
          CREATE INDEX IF NOT EXISTS agent_observations_by_system
            ON agent_observations(system_id,created_at);
          CREATE TABLE IF NOT EXISTS agent_trigger_observations(
            trigger_id TEXT PRIMARY KEY REFERENCES agent_triggers(id),
            observation_id TEXT NOT NULL REFERENCES agent_observations(id));
        """)
        self.conn.commit()

    def close(self):
        self.identities.close()
        self.workspace.close()

    def _principal(self, token, system_id, action="read"):
        principal = self.identities.authenticate(token)
        self.identities.authorize(principal, action)
        self.workspace.one("systems", system_id)
        if principal["role"] != "admin":
            row = self.conn.execute(
                "SELECT 1 FROM agent_system_grants WHERE username=? AND system_id=?",
                (principal["username"],system_id)).fetchone()
            if not row:
                raise AuthenticationError("No grant to this system")
        return principal

    def grant_system(self, admin_token, username, system_id):
        principal = self.identities.authenticate(admin_token)
        self.identities.authorize(principal,"users")
        self.workspace.one("systems",system_id)
        if not self.identities.conn.execute(
            "SELECT 1 FROM hq_identities WHERE username=? AND active=1",(username,)).fetchone():
            raise ValueError("Unknown or inactive user")
        with self.conn:
            self.conn.execute("INSERT OR IGNORE INTO agent_system_grants VALUES(?,?)",
                              (username,system_id))
            self.workspace._audit(principal["username"],"agent.system_granted",
                                  system_id,{"recipient":username})
        return {"username":username,"system_id":system_id,"granted":True}

    def revoke_system(self, admin_token, username, system_id):
        principal=self.identities.authenticate(admin_token)
        self.identities.authorize(principal,"users")
        with self.conn:
            self.conn.execute("DELETE FROM agent_system_grants WHERE username=? AND system_id=?",
                              (username,system_id))
            self.workspace._audit(principal["username"],"agent.system_revoked",
                                  system_id,{"recipient":username})

    def system_context(self, token, system_id, limit=10):
        """Return only metadata/outcomes, never raw fixtures or observation values."""
        self._principal(token,system_id)
        if type(limit) is not int or not 1 <= limit <= READ_LIMIT:
            raise ValueError("History limit must be in 1..50")
        system=self.workspace.one("systems",system_id)
        protocols=self.conn.execute(
            "SELECT id,version,state,digest,created_at FROM protocols WHERE system_id=?"
            " ORDER BY version DESC LIMIT ?",(system_id,limit)).fetchall()
        runs=self.conn.execute("""
            SELECT r.id,r.protocol_id,r.results,r.result_digest,r.created_at
              FROM runs r JOIN protocols p ON p.id=r.protocol_id
             WHERE p.system_id=? ORDER BY r.created_at DESC,r.rowid DESC LIMIT ?""",
             (system_id,limit)).fetchall()
        snapshots=[]
        for row in runs:
            result=json.loads(row["results"])
            if digest(encode(result))!=row["result_digest"]:
                raise ValueError("Stored qualification run digest mismatch")
            observations=result.get("results",[])
            snapshots.append({
                "run_id":row["id"],"protocol_id":row["protocol_id"],
                "result_digest":row["result_digest"],"created_at":row["created_at"],
                "summary":{key:int(value) for key,value in result.get("summary",{}).items()
                           if key in {"PASS","FAIL","ERROR","NOT_RUN"}},
                "test_statuses":[{"id":t["id"],"status":t["status"],
                                  "evidence_ref":t.get("evidence_ref")}
                                 for t in observations]
            })
        deviations=self.conn.execute("""
            SELECT d.id,d.run_id,d.test_id,d.kind,d.status,d.retest_run_id
              FROM deviations d JOIN runs r ON r.id=d.run_id
              JOIN protocols p ON p.id=r.protocol_id
             WHERE p.system_id=? ORDER BY d.updated_at DESC LIMIT ?""",
             (system_id,limit)).fetchall()
        return {
            "system":{"id":system["id"],"name":system["name"],
                      "intended_use":system["intended_use"]},
            "protocols":[dict(row) for row in protocols],
            "runs":snapshots,"deviations":[dict(d) for d in deviations],
            "scope":"REDACTED_METADATA_ONLY","qualification_approved":False
        }

    @staticmethod
    def historical_findings(context):
        """Compare adjacent runs only when test identity persists; no causal claims."""
        runs=context["runs"]
        findings=[]
        if not runs:
            findings.append({"code":"NO_HISTORICAL_RUNS","severity":"review",
                             "message":"No verified workspace run history available",
                             "source_refs":["system:"+context["system"]["id"]]})
            return findings
        latest=runs[0]
        previous=runs[1] if len(runs)>1 else None
        if previous:
            before={x["id"]:x["status"] for x in previous["test_statuses"]}
            for now in latest["test_statuses"]:
                old=before.get(now["id"])
                if old=="PASS" and now["status"]!="PASS":
                    findings.append({
                        "code":"STATUS_REGRESSION","severity":"high",
                        "message":"Previously passing test has a nonpassing later outcome; cause unknown",
                        "source_refs":["test:"+now["id"],"run:"+latest["run_id"],
                                       "run:"+previous["run_id"]]})
                elif old in {"FAIL","ERROR","NOT_RUN"} and now["status"] in {"FAIL","ERROR","NOT_RUN"}:
                    findings.append({
                        "code":"PERSISTENT_FAILURE","severity":"review",
                        "message":"Nonpassing test recurred in two runs; cause unknown",
                        "source_refs":["test:"+now["id"],"run:"+latest["run_id"],
                                       "run:"+previous["run_id"]]})
        pending=[d for d in context["deviations"] if d["status"]!="RESOLVED"]
        if pending:
            findings.append({"code":"OPEN_DEVIATIONS","severity":"review",
                             "message":str(len(pending))+" unresolved deviation records in retrieved history",
                             "source_refs":["deviation:"+x["id"] for x in pending]})
        return findings

    def analyze(self, token, system_id, protocol, agent, *,
                changed_files=None, registry=None, evidence_dir=None,
                trusted_manifest_sha256=None):
        actor=self._principal(token,system_id)
        if agent not in AGENTS:
            raise ValueError("Unknown agent")
        validate_v3(protocol)
        if protocol["system"]["id"]!=system_id:
            raise ValueError("Protocol belongs to a different system")
        start=time.perf_counter()
        context=self.system_context(token,system_id)
        report=investigate(agent,protocol,changed_files=changed_files,
                           registry=registry,evidence_dir=evidence_dir,
                           trusted_manifest_sha256=trusted_manifest_sha256)
        extras=self.historical_findings(context)
        # These are optional contextual observations, never silently turned
        # into protocol execution facts or model-backed root-cause claims.
        if agent in {"failure-investigation","gap-hunter","release-impact","qa-readiness"}:
            report["findings"].extend(extras)
        report["context"]={
            "historical_runs":len(context["runs"]),
            "protocol_versions":len(context["protocols"]),
            "unresolved_deviations":sum(x["status"]!="RESOLVED" for x in context["deviations"]),
            "data_scope":"metadata_only"
        }
        report["qualification_approved"]=False
        report["human_review_required"]=True
        elapsed=(time.perf_counter()-start)*1000
        report_text=encode(report).decode()
        uid=str(uuid.uuid4())
        with self.conn:
            self.conn.execute("""INSERT INTO agent_observations
              VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
              (uid,system_id,actor["username"],agent,"DRAFT",
               digest(encode(protocol)),_utc(),elapsed,"none",report_text,
               digest(report_text.encode())))
            self.conn.execute("INSERT INTO agent_review_queue(observation_id) VALUES(?)",(uid,))
            self.workspace._audit(actor["username"],"agent.draft_created",uid,
                                  {"agent":agent,"system_id":system_id})
        return {"id":uid,"agent":agent,"status":"DRAFT",
                "elapsed_ms":round(elapsed,3),"report":report}

    def review(self, token, observation_id, decision, rationale):
        if decision not in REVIEW_STATES or not isinstance(rationale,str) or not 8<=len(rationale.strip())<=1000:
            raise ValueError("Explicit review decision and rationale required")
        row=self.conn.execute(
            "SELECT system_id,report,report_digest,actor FROM agent_observations WHERE id=?",
            (observation_id,)).fetchone()
        if not row:
            raise KeyError("Unknown observation")
        actor=self._principal(token,row["system_id"],"baseline")
        if actor["username"]==row["actor"]:
            raise AuthenticationError("Draft author cannot review own finding")
        if digest(row["report"].encode())!=row["report_digest"]:
            raise ValueError("Observation digest mismatch")
        with self.conn:
            changed=self.conn.execute("""UPDATE agent_review_queue
               SET disposition=?,reviewer=?,rationale=?,reviewed_at=?
               WHERE observation_id=? AND disposition='PENDING'""",
               (decision,actor["username"],rationale.strip(),_utc(),observation_id))
            if changed.rowcount!=1:
                raise ValueError("Observation has already been reviewed")
            self.workspace._audit(actor["username"],"agent.draft_reviewed",observation_id,
                                  {"decision":decision})
        return {"observation_id":observation_id,"decision":decision,
                "qualification_approved":False}

    def trigger(self, token, system_id, event_type, event_key, payload):
        principal=self._principal(token,system_id,"execute")
        if event_type not in EVENT_TYPES or not isinstance(event_key,str) or not 8<=len(event_key)<=128:
            raise ValueError("Invalid event")
        if not isinstance(payload,dict) or len(encode(payload))>4096:
            raise ValueError("Bounded event metadata required")
        if any(k not in {"source_sha","run_id","protocol_digest","source_ref"} for k in payload):
            raise ValueError("No arbitrary or sensitive event payloads")
        payload_hash=digest(encode(payload))
        old=self.conn.execute("""SELECT * FROM agent_triggers
            WHERE system_id=? AND event_type=? AND event_key=?""",
            (system_id,event_type,event_key)).fetchone()
        if old:
            if old["payload_digest"]!=payload_hash:
                raise ValueError("Idempotency key reused with different event")
            return {"id":old["id"],"state":old["state"],"duplicate":True}
        uid=str(uuid.uuid4())
        with self.conn:
            self.conn.execute("""INSERT INTO agent_triggers VALUES(?,?,?,?,?,?,?,?)""",
                (uid,system_id,event_type,event_key,payload_hash,
                 principal["username"],"REVIEW_PENDING",_utc()))
            self.workspace._audit(principal["username"],"agent.trigger_recorded",
                                  uid,{"type":event_type,"system_id":system_id})
        return {"id":uid,"state":"REVIEW_PENDING","duplicate":False}

    def process_trigger(self, token, trigger_id, protocol, *, changed_files=None, registry=None):
        """Run one bounded advisory investigation for a recorded local event.

        No autonomous agent tool loop, no source edits, no qualification approval.
        Failed execution leaves a visible FAILED trigger; no silent retries.
        """
        row=self.conn.execute("SELECT * FROM agent_triggers WHERE id=?",(trigger_id,)).fetchone()
        if not row:
            raise KeyError("Unknown trigger")
        actor=self._principal(token,row["system_id"],"execute")
        if row["state"]!="REVIEW_PENDING":
            raise ValueError("Trigger has already been processed")
        agent={"RELEASE_CHANGED":"release-impact",
               "QUALIFICATION_FAILED":"failure-investigation",
               "COVERAGE_GAP":"gap-hunter"}[row["event_type"]]
        try:
            if row["event_type"]=="RELEASE_CHANGED" and not changed_files:
                raise ValueError("Explicit changed paths required")
            result=self.analyze(token,row["system_id"],protocol,agent,
                                changed_files=changed_files,registry=registry)
        except Exception:
            with self.conn:
                self.conn.execute("UPDATE agent_triggers SET state='FAILED' WHERE id=? AND state='REVIEW_PENDING'",
                                  (trigger_id,))
                self.workspace._audit(actor["username"],"agent.trigger_failed",trigger_id,
                                      {"agent":agent})
            raise
        with self.conn:
            self.conn.execute("INSERT INTO agent_trigger_observations VALUES(?,?)",
                              (trigger_id,result["id"]))
            self.conn.execute("UPDATE agent_triggers SET state='DRAFT_READY' WHERE id=?",
                              (trigger_id,))
            self.workspace._audit(actor["username"],"agent.trigger_processed",trigger_id,
                                  {"observation_id":result["id"]})
        return {"trigger_id":trigger_id,"observation_id":result["id"],
                "state":"DRAFT_READY","qualification_approved":False}

    def review_queue(self, token, system_id, limit=30):
        self._principal(token,system_id,"baseline")
        if type(limit) is not int or not 1<=limit<=READ_LIMIT:
            raise ValueError("Invalid review page limit")
        rows=self.conn.execute("""
          SELECT o.id,o.agent,o.actor,o.created_at,o.elapsed_ms,q.disposition
          FROM agent_observations o JOIN agent_review_queue q
          ON o.id=q.observation_id
          WHERE o.system_id=? ORDER BY o.created_at DESC,o.rowid DESC LIMIT ?""",
          (system_id,limit)).fetchall()
        return [dict(x) for x in rows]

    def metrics(self, token, system_id):
        self._principal(token,system_id,"read")
        rows=self.conn.execute("""SELECT agent,status,elapsed_ms,model FROM agent_observations
                                   WHERE system_id=?""",(system_id,)).fetchall()
        from statistics import median
        return {"system_id":system_id,"completed_drafts":sum(r["status"]=="DRAFT" for r in rows),
                "agents":{a:sum(r["agent"]==a for r in rows) for a in AGENTS},
                "median_duration_ms":round(median([r["elapsed_ms"] for r in rows]),3) if rows else None,
                "model_invocations":sum(r["model"]!="none" for r in rows),
                "model_validation_performed":False,
                "regulated_evidence":False}
