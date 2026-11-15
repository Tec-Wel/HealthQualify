"""Regression suite for stricter qualification and lifecycle tooling."""
import copy
import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from healthqualify.protocol_v3 import validate_v3, execute_v3
from healthqualify.change_graph import plan_requalification
from healthqualify.evidence_v3 import export_v3, verify_v3
from healthqualify.assurance_profiles import plan
from healthqualify.ai_providers import Draft, DisabledProvider, draft
from healthqualify.backup import backup_sqlite, verify_backup
from healthqualify.benchmark import run_internal_fixture

ROOT=Path(__file__).resolve().parents[1]
DEMO=ROOT/"examples"/"synthetic_lis_v3"/"protocol.json"
V2=ROOT/"examples"/"synthetic_lis_v2"/"protocol.json"

class ContractV3Tests(unittest.TestCase):
    def setUp(self):
        self.doc=json.loads(DEMO.read_text())

    def test_runner_provenance_and_intended_seeded_failures(self):
        validate_v3(self.doc)
        result=execute_v3(self.doc)
        self.assertEqual(result["summary"]["FAIL"],5)
        self.assertEqual(result["summary"]["PASS"],2)
        self.assertFalse(result["qualification_approved"])
        self.assertEqual(result["build_sha"],"a"*40)

    def test_rejects_unknown_or_unsourced_requirements(self):
        bad=copy.deepcopy(self.doc)
        bad["tests"][0]["magic_python"]="print('not allowed')"
        with self.assertRaises(ValueError):
            validate_v3(bad)
        bad=copy.deepcopy(self.doc)
        bad["requirements"][0]["source_id"]="UNKNOWN"
        with self.assertRaises(ValueError):
            validate_v3(bad)

    def test_runner_must_be_offline(self):
        bad=copy.deepcopy(self.doc)
        bad["execution_policy"]["network"]=True
        with self.assertRaises(ValueError):
            validate_v3(bad)
        bad=copy.deepcopy(self.doc)
        bad["approval_reference"]="fabricated"
        with self.assertRaises(ValueError):
            validate_v3(bad)

    def test_impact_known_and_unknown(self):
        known=plan_requalification(self.doc,["healthqualify/healthcare.py"])
        self.assertEqual(known["impact"],"REVIEW_REQUIRED")
        self.assertEqual(len(known["recommended_test_ids"]),2)
        unknown=plan_requalification(self.doc,["another-folder/untested.py"])
        self.assertEqual(unknown["impact"],"UNKNOWN_IMPACT")
        self.assertEqual(len(unknown["recommended_test_ids"]),7)
        self.assertFalse(unknown["qualification_approved"])
        with self.assertRaises(ValueError):
            plan_requalification(self.doc,["../escape"])

    def test_verified_manifest_rejects_substitution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"run"
            receipt=export_v3(DEMO.read_bytes(),root)
            trusted=receipt["manifest_sha256"]
            self.assertTrue(verify_v3(root,trusted))
            self.assertFalse(verify_v3(root,"0"*64))
            (root/"results.json").write_text("{}")
            self.assertFalse(verify_v3(root,trusted))

    def test_profiles_never_autocertify(self):
        selected=plan({"intended_use":"Synthetic LIS"},
                      {"us-part-11":"UNDETERMINED"},"CSA")
        self.assertEqual(selected["approval"],"DRAFT")
        self.assertFalse(selected["legal_determination"])
        with self.assertRaises(ValueError):
            plan({"intended_use":"Synthetic LIS"},{"invented":"APPLICABLE"},"CSA")

    def test_ai_provider_rejects_forged_pass(self):
        with self.assertRaises(RuntimeError):
            draft(DisabledProvider(),"oq","synthetic requirement")
        class Forged:
            def suggest(self,role,text):
                return Draft("bad",role,"Everything passed",approved=True)
        with self.assertRaises(ValueError):
            draft(Forged(),"oq","synthetic requirement")

    def test_backup_is_consistent_and_detects_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=Path(tmp)/"source.db"
            con=sqlite3.connect(src)
            con.execute("CREATE TABLE example (id INTEGER PRIMARY KEY, status TEXT)")
            con.execute("INSERT INTO example(status) VALUES (?)",("synthetic",))
            con.commit()
            dest=Path(tmp)/"backup.db"
            rec=backup_sqlite(src,dest)
            self.assertTrue(verify_backup(dest,rec["sha256"]))
            self.assertFalse(verify_backup(dest,"0"*64))
            with self.assertRaises(ValueError):
                backup_sqlite(src,dest)
            con.close()

    def test_benchmark_stays_internal(self):
        r=run_internal_fixture(V2)
        self.assertEqual(r["failures"],5)
        self.assertFalse(r["claim_of_competitor_superiority"])
        self.assertEqual(r["comparison_status"],"NOT_RUN")

if __name__=="__main__":
    unittest.main()
