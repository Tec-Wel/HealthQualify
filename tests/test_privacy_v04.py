"""Privacy minimization and fail-closed customer release gate regression tests."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from healthqualify.privacy import minimize_result, release_readiness
from healthqualify.assurance import assess_v2
from healthqualify.workspace import Workspace

EXAMPLE=Path(__file__).resolve().parents[1]/"examples"/"synthetic_lis_v2"/"protocol.json"

class PrivacyReleaseTests(unittest.TestCase):
    def test_redaction_keeps_outcomes_without_raw_observations(self):
        doc=json.loads(EXAMPLE.read_text())
        report=assess_v2(doc)
        masked=minimize_result(report)
        self.assertEqual(masked["summary"],report["summary"])
        self.assertFalse(masked["qualification_approved"])
        self.assertTrue(all(x["actual"]=="[WITHHELD]" for x in masked["results"]))
        self.assertTrue(all(x["expected"]=="[WITHHELD]" for x in masked["results"]))

    def test_workspace_does_not_persist_actual_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            w=Workspace(Path(tmp)/"hq.db")
            s=w.add_system("Synthetic LIS","Demo","Author")
            doc=json.loads(EXAMPLE.read_text())
            doc["system"]["id"]=s["id"]
            p=w.draft_protocol(s["id"],doc,"Author")
            w.baseline(p["id"],"QA","Synthetic review")
            run=w.execute(p["id"],"Author")
            self.assertTrue(all(x["actual"]=="[WITHHELD]" for x in run["results"]["results"]))
            w.close()

    def test_regulated_release_never_automatically_approved(self):
        result=release_readiness({"identity_proofing":"DOC-123"})
        self.assertEqual(result["technical_release_gate"],"BLOCKED")
        self.assertFalse(result["regulated_use_approved"])
        self.assertGreaterEqual(len(result["criteria"]),8)
        self.assertEqual(result["criteria"]["identity_proofing"]["status"],"REVIEW_REQUIRED")

if __name__=="__main__":
    unittest.main()
