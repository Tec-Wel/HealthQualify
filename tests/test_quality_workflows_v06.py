"""Tests for controlled review, release impact, retention and QMS export."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from healthqualify.workspace import Workspace
from healthqualify.security import IdentityStore,AuthenticationError
from healthqualify.deviation_review import DeviationReview
from healthqualify.release_qualification import ReleaseDecisions,release_plan
from healthqualify.release_ci import advisory
from healthqualify.retention import RetentionStore

ROOT=Path(__file__).resolve().parents[1]
DEMO=json.loads((ROOT/"examples"/"synthetic_lis_v2"/"protocol.json").read_text())
V3=json.loads((ROOT/"examples"/"synthetic_lis_v3"/"protocol.json").read_text())
H1="a"*40
H2="b"*40

class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.db=str(Path(self.temp.name)/"test.db")
        w=Workspace(self.db)
        self.system=w.add_system("Demo LIS","Synthetic only","author")
        self.protocol=dict(DEMO)
        self.protocol["system"]={**DEMO["system"],"id":self.system["id"]}
        p=w.draft_protocol(self.system["id"],self.protocol,"author")
        w.baseline(p["id"],"qa_user","Synthetic baseline only")
        self.run=w.execute(p["id"],"author")
        self.deviation=next(d for d in w.list("deviations") if d["test_id"]=="OQ-001")
        w.close()
        ids=IdentityStore(self.db)
        ids.bootstrap("admin_user","strong-administrator-passphrase")
        actor=ids.authenticate(ids.login("admin_user","strong-administrator-passphrase"))
        ids.create_user(actor,"qa_user","quality-review-password","qa")
        ids.create_user(actor,"writer_user","synthetic-author-password","validator")
        ids.close()
    def tearDown(self):
        self.temp.cleanup()

    def test_qa_approval_is_review_not_resolution(self):
        review=DeviationReview(self.db)
        try:
            ref=next(t["evidence_ref"] for t in self.run["results"]["results"] if t["id"]=="OQ-001")
            with self.assertRaises(AuthenticationError):
                review.submit("writer_user","synthetic-author-password",
                              self.deviation["id"],"RETEST_REQUIRED","Failed criterion",ref)
            with self.assertRaises(ValueError):
                review.submit("qa_user","quality-review-password",self.deviation["id"],
                              "RETEST_REQUIRED","Failed criterion","hq-run:forged/test/OQ-001")
            # Even an authentic PASS from the same run cannot justify an
            # unrelated failed deviation.
            unrelated=next(t["evidence_ref"] for t in self.run["results"]["results"]
                           if t["id"]=="IQ-001")
            with self.assertRaises(ValueError):
                review.submit("qa_user","quality-review-password",self.deviation["id"],
                              "RETEST_REQUIRED","Incorrect evidence target",unrelated)
            receipt=review.submit("qa_user","quality-review-password",self.deviation["id"],
                                  "RETEST_REQUIRED","Recheck the laboratory identity contract",ref)
            self.assertEqual(receipt["record"]["qualification_approved"],False)
            self.assertEqual(review.work.one("deviations",self.deviation["id"])["status"],"IN_REVIEW")
            handoff=review.qms_export(self.deviation["id"])
            self.assertEqual(len(handoff["package"]["review_records"]),1)
            self.assertEqual(handoff["package"]["protocol_digest"],self.run["results"]["protocol_digest"])
            with self.assertRaises(ValueError):
                review.submit("qa_user","quality-review-password",self.deviation["id"],
                              "RETEST_REQUIRED","Incorrect","hq-run:forged/test/OQ-001")
        finally:
            review.close()

    def test_retention_detects_mutation_and_keeps_hold(self):
        with tempfile.TemporaryDirectory() as folder:
            store=RetentionStore(Path(folder)/"vault")
            try:
                record=store.add(b'{"synthetic":true}',"qms_handoff",retention_days=730,legal_hold=True)
                self.assertTrue(store.verify(record["id"]))
                self.assertTrue(store.inventory()[0]["legal_hold"])
                file=Path(folder)/"vault"/"artifacts"/(record["id"]+".bin")
                file.write_bytes(b'{"synthetic":false}')
                self.assertFalse(store.verify(record["id"]))
                with self.assertRaises(ValueError):
                    store.add(b"123","patient_record")
            finally:store.close()

class ReleaseTests(unittest.TestCase):
    @patch("healthqualify.release_qualification.subprocess.run")
    def test_release_mapping_and_unknown(self,runner):
        runner.return_value=subprocess.CompletedProcess([],0,"healthqualify/healthcare.py\n","")
        plan=release_plan(V3,H1,H2)
        self.assertEqual(plan["plan"]["impact"]["impact"],"REVIEW_REQUIRED")
        self.assertTrue(plan["plan"]["human_review_required"])
        runner.return_value=subprocess.CompletedProcess([],0,"new/unknown.py\n","")
        missing=release_plan(V3,H1,H2)
        self.assertEqual(missing["plan"]["impact"]["impact"],"UNKNOWN_IMPACT")
        self.assertEqual(len(missing["plan"]["impact"]["recommended_test_ids"]),7)

    def test_qa_decisions_never_mark_release_qualified(self):
        with tempfile.TemporaryDirectory() as folder:
            database=str(Path(folder)/"reviews.db")
            ids=IdentityStore(database)
            ids.bootstrap("admin_user","long-strong-administrator-pass")
            admin=ids.authenticate(ids.login("admin_user","long-strong-administrator-pass"))
            ids.create_user(admin,"review_qa","long-quality-review-password","qa")
            ids.create_user(admin,"ordinary","long-writer-password-123","validator")
            ids.close()
            with patch("healthqualify.release_qualification.subprocess.run") as runner:
                runner.return_value=subprocess.CompletedProcess([],0,"healthqualify/healthcare.py\n","")
                plan=release_plan(V3,H1,H2)["plan"]
            log=ReleaseDecisions(database)
            try:
                with self.assertRaises(AuthenticationError):
                    log.record(plan,"ordinary","long-writer-password-123","BLOCKED","Need retest")
                with self.assertRaises(ValueError):
                    log.record(plan,"review_qa","long-quality-review-password","APPROVED","Seems good")
                outcome=log.record(plan,"review_qa","long-quality-review-password",
                                   "RETEST_REQUIRED","Require OQ retest evidence")
                self.assertFalse(outcome["qualification_approved"])
                self.assertEqual(outcome["record"]["head_sha"],H2)
            finally:log.close()

    @patch("healthqualify.release_ci._git")
    def test_first_release_unknown(self,git):
        def handler(*args):
            if args[0]=="describe":raise subprocess.CalledProcessError(128,args)
            return H2
        git.side_effect=handler
        answer=advisory(V3,"v0.6.0")
        self.assertEqual(answer["plan"]["impact"]["impact"],"UNKNOWN_IMPACT")
        self.assertFalse(answer["plan"]["qualification_approved"])

if __name__=="__main__":
    unittest.main()
