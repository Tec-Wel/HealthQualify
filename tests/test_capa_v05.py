"""CAPA investigation and controlled retesting regression checks."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from healthqualify.capa import CAPA

BASE=Path(__file__).resolve().parents[1]/"examples"/"synthetic_lis_v2"/"protocol.json"

class CAPATests(unittest.TestCase):
    def test_closure_requires_unchanged_criteria_and_proven_retest(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=CAPA(str(Path(tmp)/"data.db"))
            try:
                s=db.work.add_system("LIS synthetic","Test-only","Author")
                spec=json.loads(BASE.read_text())
                spec["system"]["id"]=s["id"]
                old=db.work.draft_protocol(s["id"],spec,"Author")
                db.work.baseline(old["id"],"QA","Reviewed synthetic test")
                first=db.work.execute(old["id"],"Author")
                failure=next(x for x in db.work.list("deviations")
                             if x["run_id"]==first["id"] and x["test_id"]=="OQ-001")
                case=db.open_case(failure["id"],"Engineer","high","Engineer")
                with self.assertRaises(ValueError):
                    db.close_case(case["id"],"Engineer",first["id"],"evidence")
                db.investigate(case["id"],"Synthetic identifier mismatch","Correct fixture",
                               "New result must match the original requirement","Engineer")
                with self.assertRaises(ValueError):
                    db.close_case(case["id"],"QA",first["id"],"evidence")
                corrected=copy.deepcopy(spec)
                corrected["fixtures"]["hl7_oru"]=corrected["fixtures"]["hl7_oru"].replace(
                    "P999^^^HOSP^MR","P123^^^HOSP^MR")
                upgraded=db.work.draft_protocol(s["id"],corrected,"Author")
                db.work.baseline(upgraded["id"],"QA","Approved synthetic retest fixture")
                rerun=db.work.execute(upgraded["id"],"Author")
                closed=db.close_case(case["id"],"QA",rerun["id"],"RETEST-RUN-2")
                self.assertEqual(closed["status"],"CLOSED")
                self.assertEqual(closed["retest_run_id"],rerun["id"])
                altered=copy.deepcopy(corrected)
                next(x for x in altered["tests"] if x["id"]=="OQ-001")["expected"]="different"
                changed=db.work.draft_protocol(s["id"],altered,"Author")
                db.work.baseline(changed["id"],"QA","Test criteria changed")
                third=db.work.execute(changed["id"],"Author")
                second_case=db.open_case(failure["id"],"Engineer","high","Engineer")
                db.investigate(second_case["id"],"Mismatch","Fix","Proof","Engineer")
                with self.assertRaises(ValueError):
                    db.close_case(second_case["id"],"QA",third["id"],"RETEST-3")
            finally:
                db.close()

if __name__=="__main__":
    unittest.main()
