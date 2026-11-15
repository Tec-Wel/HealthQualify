"""Offline and negative-path tests for the five advisory agents."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from healthqualify.agents import AGENTS, investigate, load_protocol
from healthqualify.evidence_v3 import export_v3

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_FILE = ROOT / "examples/synthetic_lis_v3/protocol.json"


class AgentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.protocol = load_protocol(PROTOCOL_FILE)

    def test_agents_enumerated(self):
        self.assertEqual(len(AGENTS), 5)

    def test_release_known_mapping(self):
        report = investigate("release-impact", self.protocol,
                             changed_files=["healthqualify/healthcare.py"])
        self.assertEqual(report["summary"]["impact"]["impact"], "REVIEW_REQUIRED")
        self.assertFalse(report["qualification_approved"])
        self.assertIsNone(report["model_explanation"])

    def test_release_unknown_fails_closed(self):
        report = investigate("release-impact", self.protocol,
                             changed_files=["new/unknown.py"])
        self.assertEqual(report["summary"]["impact"]["impact"], "UNKNOWN_IMPACT")
        self.assertTrue(any(x["code"] == "UNKNOWN_IMPACT" for x in report["findings"]))

    def test_gap_without_evidence_is_not_pass(self):
        report = investigate("gap-hunter", self.protocol)
        self.assertTrue(any(x["code"] == "NO_VERIFIED_EXECUTION" for x in report["findings"]))

    def test_readiness_never_approves(self):
        report = investigate("qa-readiness", self.protocol)
        self.assertEqual(report["summary"]["readiness"], "REVIEW_BLOCKED")
        self.assertFalse(report["qualification_approved"])

    def test_failure_requires_evidence(self):
        report = investigate("failure-investigation", self.protocol)
        self.assertIsNone(report["summary"]["failure_count"])

    def test_verified_failure_analysis_and_readiness(self):
        with tempfile.TemporaryDirectory() as td:
            evidence = Path(td) / "evidence"
            info = export_v3(PROTOCOL_FILE.read_bytes(), evidence)
            failures = investigate("failure-investigation", self.protocol,
                                   evidence_dir=str(evidence),
                                   trusted_manifest_sha256=info["manifest_sha256"])
            self.assertGreater(failures["summary"]["failure_count"], 0)
            readiness = investigate("qa-readiness", self.protocol,
                                    evidence_dir=str(evidence),
                                    trusted_manifest_sha256=info["manifest_sha256"])
            self.assertEqual(readiness["summary"]["readiness"], "REVIEW_BLOCKED")

    def test_wrong_manifest_fails(self):
        with tempfile.TemporaryDirectory() as td:
            evidence = Path(td) / "evidence"
            export_v3(PROTOCOL_FILE.read_bytes(), evidence)
            with self.assertRaises(ValueError):
                investigate("gap-hunter", self.protocol, evidence_dir=str(evidence),
                            trusted_manifest_sha256="0" * 64)

    def test_missing_evidence_hash_rejected(self):
        with self.assertRaises(ValueError):
            investigate("gap-hunter", self.protocol, evidence_dir="/tmp/not-trusted")

    def test_dependencies_and_unknown(self):
        registry = {"systems": [{"id": "LIS", "components": ["healthqualify/healthcare.py"]}]}
        r = investigate("dependency-investigator", self.protocol, registry=registry,
                        changed_files=["healthqualify/healthcare.py", "new/file.py"])
        self.assertEqual(len(r["summary"]["affected_systems"]), 1)
        self.assertIn("new/file.py", r["summary"]["unmapped_components"])

    def test_duplicate_registry_system_denied(self):
        registry = {"systems": [
            {"id": "LIS", "components": ["healthqualify/healthcare.py"]},
            {"id": "LIS", "components": ["healthqualify/healthcare.py"]}]}
        with self.assertRaises(ValueError):
            investigate("dependency-investigator", self.protocol, registry=registry,
                        changed_files=["healthqualify/healthcare.py"])

    def test_no_network_or_model_by_default(self):
        with patch("healthqualify.agents.local_draft", side_effect=AssertionError("called")):
            r = investigate("gap-hunter", self.protocol)
        self.assertIsNone(r["model_explanation"])

    def test_opt_in_local_model_cannot_override_findings(self):
        with patch("healthqualify.agents.local_draft",
                   return_value={"status": "DRAFT_UNVERIFIED",
                                 "text": "The model says all tests passed."}):
            result = investigate("qa-readiness", self.protocol, use_ollama=True)
        self.assertFalse(result["qualification_approved"])
        self.assertEqual(result["summary"]["readiness"], "REVIEW_BLOCKED")
        self.assertTrue(result["findings"])

    def test_unsafe_path_rejected(self):
        with self.assertRaises(ValueError):
            investigate("release-impact", self.protocol, changed_files=["../escape"])

    def test_non_synthetic_ai_denied(self):
        protocol = json.loads(json.dumps(self.protocol))
        protocol["execution_policy"]["data_classification"] = "public"
        with self.assertRaises(ValueError):
            investigate("gap-hunter", protocol, use_ollama=True)


if __name__ == "__main__":
    unittest.main()
