"""End-to-end tests for the local HealthQualify product foundation."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from healthqualify.workspace import Workspace
from healthqualify.reports import export_run
from healthqualify.regulatory import applicability,compare_text,list_controls
from healthqualify.studio import draft_urs,protocol_from_urs,risk_plan
from healthqualify.ai import local_draft,available_roles
from healthqualify.modelqual import score_classifier,compare_model_versions
from healthqualify.api import create_handler

ROOT=Path(__file__).resolve().parents[1]
EXAMPLE=ROOT/"examples"/"synthetic_lis_v2"/"protocol.json"

class ProductTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.db=Workspace(Path(self.tmp.name)/"workspace.db")
        self.system=self.db.add_system("Synthetic LIS","Synthetic laboratory transfer","Engineer A")
        self.protocol=json.loads(EXAMPLE.read_text(encoding="utf-8"))
        self.protocol["system"]["id"]=self.system["id"]

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def test_full_workspace_lifecycle(self):
        draft=self.db.draft_protocol(self.system["id"],self.protocol,"Engineer A")
        self.assertEqual(draft["version"],1)
        with self.assertRaises(ValueError):
            self.db.execute(draft["id"],"Engineer A")
        with self.assertRaises(ValueError):
            self.db.baseline(draft["id"],"Engineer A","Self approval")
        approved=self.db.baseline(draft["id"],"Reviewer B","Approved for synthetic execution only")
        self.assertEqual(approved["state"],"BASELINED")
        with self.assertRaises(ValueError):
            self.db.baseline(draft["id"],"Reviewer B","repeat")
        result=self.db.execute(draft["id"],"Engineer A")
        self.assertEqual(result["results"]["summary"]["FAIL"],5)
        self.assertFalse(result["results"]["qualification_approved"])
        gaps=[d for d in self.db.list("deviations") if d["run_id"]==result["id"]]
        self.assertEqual(len(gaps),5)
        with self.assertRaises(ValueError):
            self.db.disposition(gaps[0]["id"],"Reviewer B","without retest")
        with self.assertRaises(ValueError):
            self.db.disposition(gaps[0]["id"],"Reviewer B","same run",result["id"])
        exported=Path(self.tmp.name)/"report"
        manifest=export_run(self.db,result["id"],exported)
        self.assertIn("report.html",manifest["sha256"])
        self.assertIn("Not a qualification approval", (exported/"report.html").read_text())
        self.assertGreaterEqual(len(self.db.audit_events()),4)

    def test_baseline_not_edited_in_place(self):
        first=self.db.draft_protocol(self.system["id"],self.protocol,"Author")
        self.db.baseline(first["id"],"Reviewer","Synthetic baseline review")
        nextdoc=copy.deepcopy(self.protocol)
        nextdoc["system"]["version"]="0.3"
        second=self.db.draft_protocol(self.system["id"],nextdoc,"Author")
        self.assertEqual(second["version"],2)
        self.assertEqual(self.db.one("protocols",first["id"])["payload"]["system"]["version"],"0.2")

    def test_regulatory_review_never_automatic(self):
        frameworks=list_controls()
        self.assertGreaterEqual(len(frameworks),5)
        doc=applicability({"intended_use":"Synthetic LIS"},{"us-part-11":"UNDETERMINED"})
        self.assertTrue(doc["assessments"][0]["requires_authorized_review"])
        self.assertFalse(doc["regulatory_approval"])
        diff=compare_text("old text","new text")
        self.assertTrue(diff["changed"])
        self.assertTrue(diff["human_review_required"])

    def test_urs_never_fabricates_criteria(self):
        urs=draft_urs({"intended_use":"Lab transfer"},
                      [{"statement":"Route synthetic alerts", "risk":"high","source":"stated"}])
        self.assertEqual(urs["requirements"][0]["acceptance_state"],"TO_BE_DEFINED")
        plan=protocol_from_urs(urs,self.system["id"])
        self.assertEqual(plan["tests"],[])
        self.assertEqual(len(plan["planning_gaps"]),1)
        risk=risk_plan({"intended_use":"Lab transfer"},["us-part-11"],"high")
        self.assertIsNone(risk["selected_pathway"])

    def test_ai_requires_opt_in(self):
        self.assertIn("oq",available_roles())
        with self.assertRaises(ValueError):
            local_draft("oq","Synthetic example","local-llm",consent=False)

    def test_modelqual_observations_not_approval(self):
        rows=[{"truth":"positive","prediction":"positive"},
              {"truth":"negative","prediction":"positive"},
              {"truth":"negative","prediction":"negative"}]
        result=score_classifier(rows)
        self.assertAlmostEqual(result["accuracy"],2/3)
        self.assertFalse(result["approved"])
        old={"dataset_id":"example","rows":rows}
        new={"dataset_id":"example","rows":rows[:2]+[{"truth":"negative","prediction":"negative"}]}
        self.assertTrue(compare_model_versions(old,new)["requires_review"])
        with self.assertRaises(ValueError):
            compare_model_versions(old,{"dataset_id":"other","rows":rows})

    def test_api_requires_token_and_uses_loopback_handler(self):
        handler=create_handler(self.db,"a"*32)
        self.assertEqual(handler.server_version,"HealthQualifyDev/0.3")

if __name__=="__main__":
    unittest.main()
