"""Bounded offline agent orchestration with append-only local development history.

No network dependency. Agent findings and histories are advisory, never regulated
electronic records, authoritative test results, signatures, or formal approvals.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .agents import AGENTS, investigate, load_protocol, load_registry
from .assurance import encode

MAX_HISTORY = 250
ALL_AGENTS = tuple(AGENTS)


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def _require_id(value):
    if not isinstance(value, str) or not (3 <= len(value) <= 80):
        raise ValueError("actor must be a named identity of 3-80 characters")
    if not all(x.isalnum() or x in "._-@" for x in value):
        raise ValueError("actor contains unsupported characters")
    return value


class AgentHistory:
    """SQLite dev record with serialized writes and hash-chained event history.

    Hash chaining is tamper-evident only when heads are anchored externally.
    SQLite alone is not WORM storage or a Part 11-compliant audit trail.
    """
    def __init__(self, filename):
        self.conn = sqlite3.connect(str(filename), timeout=10)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("PRAGMA busy_timeout=10000")
        self.conn.executescript("""
          CREATE TABLE IF NOT EXISTS agent_jobs(
            job_id TEXT PRIMARY KEY, actor TEXT NOT NULL, agent TEXT NOT NULL,
            created_at TEXT NOT NULL, state TEXT NOT NULL,
            report_json TEXT, error TEXT);
          CREATE TABLE IF NOT EXISTS agent_events(
            id INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT NOT NULL REFERENCES agent_jobs(job_id),
            event_time TEXT NOT NULL, state TEXT NOT NULL, previous_hash TEXT NOT NULL,
            event_hash TEXT NOT NULL);
          CREATE INDEX IF NOT EXISTS ix_agent_jobs_created ON agent_jobs(created_at);
        """)
        self.conn.commit()

    def close(self):
        self.conn.close()

    def _transition(self, job_id, state, report=None, error=None):
        previous = self.conn.execute(
            "SELECT event_hash FROM agent_events ORDER BY id DESC LIMIT 1").fetchone()
        prior = previous[0] if previous else "0" * 64
        at = utcnow()
        serialized = json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=False) if report is not None else None
        payload = encode({"job_id": job_id, "state": state, "at": at,
                          "report_sha256": hashlib.sha256(serialized.encode()).hexdigest() if serialized else None,
                          "error": error, "previous": prior})
        event_hash = hashlib.sha256(payload).hexdigest()
        with self.conn:
            self.conn.execute("UPDATE agent_jobs SET state=?, report_json=?, error=? WHERE job_id=?",
                              (state, serialized, error, job_id))
            self.conn.execute(
                "INSERT INTO agent_events(job_id,event_time,state,previous_hash,event_hash) VALUES(?,?,?,?,?)",
                (job_id, at, state, prior, event_hash))

    def start(self, actor, agent):
        _require_id(actor)
        if agent not in AGENTS:
            raise ValueError("Unknown agent")
        job_id = str(uuid.uuid4())
        with self.conn:
            self.conn.execute("INSERT INTO agent_jobs(job_id,actor,agent,created_at,state) VALUES(?,?,?,?,?)",
                              (job_id, actor, agent, utcnow(), "QUEUED"))
        self._transition(job_id, "QUEUED")
        return job_id

    def get(self, job_id):
        row = self.conn.execute("SELECT * FROM agent_jobs WHERE job_id=?", (job_id,)).fetchone()
        if row is None:
            raise KeyError("Unknown agent job")
        result = dict(row)
        result["report"] = json.loads(result.pop("report_json")) if result["report_json"] else None
        return result

    def list(self, limit=30):
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError("Invalid history page size")
        return [self.get(x["job_id"]) for x in self.conn.execute(
            "SELECT job_id FROM agent_jobs ORDER BY created_at DESC, rowid DESC LIMIT ?", (limit,))]

    def chain_head(self):
        row = self.conn.execute("SELECT event_hash FROM agent_events ORDER BY id DESC LIMIT 1").fetchone()
        return row[0] if row else "0" * 64

    def run(self, actor, agent, protocol_path, *, changed_files=None, registry_path=None,
            evidence_dir=None, trusted_manifest_sha256=None, use_ollama=False, model="qwen3:8b"):
        """One bounded, synchronous job. Failed runs are recorded and re-raised.

        The caller is responsible for authenticating/authorizing the actor; do not
        expose this direct Python API as a multi-user service without that layer.
        """
        job_id = self.start(actor, agent)
        try:
            self._transition(job_id, "ANALYZING")
            protocol = load_protocol(protocol_path)
            registry = load_registry(registry_path) if registry_path else None
            result = investigate(agent, protocol, changed_files=changed_files, registry=registry,
                                 evidence_dir=evidence_dir,
                                 trusted_manifest_sha256=trusted_manifest_sha256,
                                 use_ollama=use_ollama, model=model)
            self._transition(job_id, "DRAFT", report=result)
        except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError, TimeoutError) as exc:
            self._transition(job_id, "FAILED", error=type(exc).__name__ + ": " + str(exc)[:300])
            raise
        return self.get(job_id)

    def run_all(self, actor, protocol_path, *, changed_files, registry_path,
                evidence_dir=None, trusted_manifest_sha256=None,
                use_ollama=False, model="qwen3:8b"):
        """Run exactly five independent analyses. No autonomous tool/action loops.

        Input validation failures are recorded per job; progress continues for the
        other agents without converting any failure to a passing outcome.
        """
        completed = []
        for agent in ALL_AGENTS:
            try:
                completed.append(self.run(
                    actor, agent, protocol_path, changed_files=changed_files,
                    registry_path=registry_path, evidence_dir=evidence_dir,
                    trusted_manifest_sha256=trusted_manifest_sha256,
                    use_ollama=use_ollama, model=model))
            except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError, TimeoutError):
                completed.append(self.list(1)[0])
        return {"jobs": completed, "chain_head": self.chain_head(),
                "qualification_approved": False, "human_review_required": True}
