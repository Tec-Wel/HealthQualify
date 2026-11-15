"""Persistence, policy and local dashboard smoke tests."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from healthqualify.agent_orchestrator import AgentHistory
from healthqualify.agent_dashboard import make_handler

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "examples/synthetic_lis_v3/protocol.json"
REGISTRY = ROOT / "examples/agents/dependencies.json"


class OrchestratorTests(unittest.TestCase):
    def test_all_five_jobs_and_persistent_history(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "agents.db"
            store = AgentHistory(db)
            result = store.run_all("local_tester", str(PROTOCOL),
                                   changed_files=["healthqualify/healthcare.py"],
                                   registry_path=str(REGISTRY))
            self.assertEqual(len(result["jobs"]), 5)
            self.assertEqual({j["agent"] for j in result["jobs"]},
                             {"release-impact","gap-hunter","failure-investigation",
                              "qa-readiness","dependency-investigator"})
            self.assertTrue(all(j["state"] == "DRAFT" for j in result["jobs"]))
            self.assertTrue(all(j["report"]["qualification_approved"] is False for j in result["jobs"]))
            self.assertEqual(len(store.list()), 5)
            head = store.chain_head()
            store.close()
            reopen = AgentHistory(db)
            self.assertEqual(head, reopen.chain_head())
            self.assertEqual(len(reopen.list()), 5)
            reopen.close()

    def test_failed_job_is_visible_and_not_approved(self):
        with tempfile.TemporaryDirectory() as td:
            store = AgentHistory(Path(td) / "jobs.db")
            with self.assertRaises(ValueError):
                store.run("local_tester", "release-impact", str(PROTOCOL),
                          changed_files=["../unsafe"])
            job = store.list(1)[0]
            self.assertEqual(job["state"], "FAILED")
            self.assertIsNone(job["report"])
            self.assertIn("ValueError", job["error"])
            store.close()

    def test_model_exception_is_recorded_as_failure(self):
        with tempfile.TemporaryDirectory() as td:
            store = AgentHistory(Path(td) / "jobs.db")
            with patch("healthqualify.agents.local_draft", side_effect=ConnectionError("offline")):
                with self.assertRaises(ConnectionError):
                    store.run("local_tester", "gap-hunter", str(PROTOCOL), use_ollama=True)
            self.assertEqual(store.list(1)[0]["state"], "FAILED")
            store.close()

    def test_dashboard_requires_auth(self):
        with tempfile.TemporaryDirectory() as td:
            store = AgentHistory(Path(td) / "jobs.db")
            handler = make_handler(store, "A" * 40, str(PROTOCOL),
                                   str(REGISTRY), ["healthqualify/healthcare.py"])
            self.assertIsNotNone(handler)
            store.close()

    def test_actor_not_arbitrary(self):
        with tempfile.TemporaryDirectory() as td:
            store = AgentHistory(Path(td) / "jobs.db")
            with self.assertRaises(ValueError):
                store.start("../admin", "gap-hunter")
            store.close()


if __name__ == "__main__":
    unittest.main()
