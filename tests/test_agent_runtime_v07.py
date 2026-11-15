"""v0.7 scoped context, historical findings, review and trigger regression tests."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from healthqualify.agent_runtime_v07 import ScopedAgentRuntime
from healthqualify.security import AuthenticationError
from healthqualify.agent_eval_v07 import evaluate

ROOT=Path(__file__).resolve().parents[1]
V2=json.loads((ROOT/"examples"/"synthetic_lis_v2"/"protocol.json").read_text())
V3=json.loads((ROOT/"examples"/"synthetic_lis_v3"/"protocol.json").read_text())

class ScopedAgentRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.runtime=ScopedAgentRuntime(Path(self.tmp.name)/"local.db")
        auth=self.runtime.identities
        auth.bootstrap("admin_user","test-admin-long-password")
        self.admin=auth.login("admin_user","test-admin-long-password")
        principal=auth.authenticate(self.admin)
        auth.create_user(principal,"qa_reviewer","test-quality-password","qa")
        auth.create_user(principal,"engineer","test-engineer-password","validator")
        auth.create_user(principal,"outsider","test-outsider-password","viewer")
        self.qa=auth.login("qa_reviewer","test-quality-password")
        self.validator=auth.login("engineer","test-engineer-password")
        self.outsider=auth.login("outsider","test-outsider-password")
        self.system=self.runtime.workspace.add_system("Synthetic LIS","Synthetic engineering only","engineer")
        self.second=self.runtime.workspace.add_system("Another demo","Synthetic only","engineer")
        self.runtime.grant_system(self.admin,"engineer",self.system["id"])
        self.runtime.grant_system(self.admin,"qa_reviewer",self.system["id"])
        self.protocol=copy.deepcopy(V3)
        self.protocol["system"]["id"]=self.system["id"]
        basic=copy.deepcopy(V2)
        basic["system"]["id"]=self.system["id"]
        draft=self.runtime.workspace.draft_protocol(self.system["id"],basic,"engineer")
        self.runtime.workspace.baseline(draft["id"],"qa_reviewer","Synthetic baseline")
        self.runtime.workspace.execute(draft["id"],"engineer")
        self.runtime.workspace.execute(draft["id"],"engineer")

    def tearDown(self):
        self.runtime.close()
        self.tmp.cleanup()

    def test_history_redacted_and_regression_is_not_root_cause(self):
        context=self.runtime.system_context(self.validator,self.system["id"])
        self.assertEqual(len(context["runs"]),2)
        self.assertEqual(context["scope"],"REDACTED_METADATA_ONLY")
        self.assertNotIn("P999",json.dumps(context))
        findings=self.runtime.historical_findings(context)
        self.assertTrue(any(x["code"]=="PERSISTENT_FAILURE" for x in findings))
        self.assertTrue(any(x["code"]=="OPEN_DEVIATIONS" for x in findings))
        report=self.runtime.analyze(self.validator,self.system["id"],self.protocol,
                                    "failure-investigation")
        self.assertFalse(report["report"]["qualification_approved"])
        self.assertEqual(report["report"]["context"]["historical_runs"],2)
        self.assertTrue(any(x["code"]=="PERSISTENT_FAILURE"
                            for x in report["report"]["findings"]))

    def test_reviewer_separation_and_duplicate_reviews(self):
        report=self.runtime.analyze(self.validator,self.system["id"],self.protocol,"gap-hunter")
        with self.assertRaises(AuthenticationError):
            self.runtime.review(self.validator,report["id"],"ACKNOWLEDGED","Reviewed evidence")
        with self.assertRaises(ValueError):
            self.runtime.review(self.qa,report["id"],"APPROVED","Do not approve")
        acknowledged=self.runtime.review(self.qa,report["id"],"NEEDS_INVESTIGATION",
                                         "Assess missing and failed test evidence")
        self.assertFalse(acknowledged["qualification_approved"])
        with self.assertRaises(ValueError):
            self.runtime.review(self.qa,report["id"],"DISMISSED","Cannot overwrite")

    def test_system_scope_denies_unauthorized_read(self):
        with self.assertRaises(AuthenticationError):
            self.runtime.system_context(self.outsider,self.system["id"])
        with self.assertRaises(AuthenticationError):
            self.runtime.system_context(self.validator,self.second["id"])
        with self.assertRaises(ValueError):
            self.runtime.analyze(self.validator,self.system["id"],V3,"gap-hunter")

    def test_triggers_idempotent_and_disallow_arbitrary_payload(self):
        event=self.runtime.trigger(self.validator,self.system["id"],"QUALIFICATION_FAILED",
                                   "run-"+"a"*16,{"run_id":"synthetic-run"})
        duplicate=self.runtime.trigger(self.validator,self.system["id"],"QUALIFICATION_FAILED",
                                       "run-"+"a"*16,{"run_id":"synthetic-run"})
        self.assertFalse(event["duplicate"])
        self.assertTrue(duplicate["duplicate"])
        with self.assertRaises(ValueError):
            self.runtime.trigger(self.validator,self.system["id"],"QUALIFICATION_FAILED",
                                 "run-"+"a"*16,{"run_id":"different"})
        with self.assertRaises(ValueError):
            self.runtime.trigger(self.validator,self.system["id"],"COVERAGE_GAP",
                                 "case-"+"b"*16,{"raw_patient_record":"NO"})
        with self.assertRaises(AuthenticationError):
            self.runtime.trigger(self.qa,self.system["id"],"COVERAGE_GAP",
                                 "case-"+"c"*16,{"source_ref":"synthetic"})

    def test_trigger_to_review_queue_and_metrics(self):
        event=self.runtime.trigger(self.validator,self.system["id"],"RELEASE_CHANGED",
                                   "commit-"+"f"*40,{"source_sha":"f"*40})
        done=self.runtime.process_trigger(self.validator,event["id"],self.protocol,
                                          changed_files=["unmapped/new.py"])
        self.assertEqual(done["state"],"DRAFT_READY")
        self.assertFalse(done["qualification_approved"])
        self.assertEqual(len(self.runtime.review_queue(self.qa,self.system["id"])),1)
        overview=self.runtime.metrics(self.validator,self.system["id"])
        self.assertEqual(overview["completed_drafts"],1)
        self.assertEqual(overview["model_invocations"],0)
        with self.assertRaises(ValueError):
            self.runtime.process_trigger(self.validator,event["id"],self.protocol,
                                         changed_files=["unmapped/new.py"])
        review=self.runtime.review(self.qa,done["observation_id"],"ACKNOWLEDGED",
                                   "Source-mapped investigation reviewed")
        self.assertFalse(review["qualification_approved"])

    def test_trigger_failure_stays_visible(self):
        event=self.runtime.trigger(self.validator,self.system["id"],"RELEASE_CHANGED",
                                   "release-"+"e"*16,{"source_sha":"e"*40})
        with self.assertRaises(ValueError):
            self.runtime.process_trigger(self.validator,event["id"],self.protocol)
        state=self.runtime.conn.execute("SELECT state FROM agent_triggers WHERE id=?",
                                       (event["id"],)).fetchone()[0]
        self.assertEqual(state,"FAILED")

    def test_grant_revoke(self):
        self.runtime.grant_system(self.admin,"outsider",self.system["id"])
        self.assertEqual(self.runtime.system_context(self.outsider,self.system["id"])["system"]["id"],
                         self.system["id"])
        self.runtime.revoke_system(self.admin,"outsider",self.system["id"])
        with self.assertRaises(AuthenticationError):
            self.runtime.system_context(self.outsider,self.system["id"])

class EvaluationTests(unittest.TestCase):
    def test_thirty_explicit_gold_label_scenarios(self):
        report=evaluate()
        self.assertEqual(report["evaluation_cases"],30)
        self.assertEqual(report["false_positive_labels"],0)
        self.assertEqual(report["missed_labels"],0)
        self.assertEqual(len(report["by_agent"]),5)
        self.assertFalse(report["model_inference_tested"])
        self.assertFalse(report["qualification_approved"])

if __name__=="__main__":
    unittest.main()
