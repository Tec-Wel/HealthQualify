"""REST isolation, evidence-link and backup-recovery tests."""
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from healthqualify.rest_local import check_local_json
from healthqualify.workspace import Workspace
from healthqualify.backup import backup_sqlite, restore_verified, verify_backup

PROTOCOL=Path(__file__).resolve().parents[1]/"examples"/"synthetic_lis_v2"/"protocol.json"

class FakeResponse:
    status=200
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self,length):return json.dumps({"status":"ok","patient":"SYNTHETIC"}).encode()
class FakeOpener:
    def open(self,request,timeout):
        if request.get_method()!="GET":
            raise AssertionError("nonread request")
        return FakeResponse()

class RESTAndRecoveryTests(unittest.TestCase):
    @patch("healthqualify.rest_local.build_opener",return_value=FakeOpener())
    def test_rest_redacted_and_consent_gated(self,opener):
        url="http://127.0.0.1:9999/test/synthetic"
        with self.assertRaises(ValueError):
            check_local_json(url,"status","ok")
        passed=check_local_json(url,"status","ok",authorized=True)
        failed=check_local_json(url,"status","bad",authorized=True)
        self.assertEqual(passed["status"],"PASS")
        self.assertEqual(failed["status"],"FAIL")
        self.assertNotIn("patient",str(passed))
        self.assertNotIn("SYNTHETIC",str(passed))
        self.assertTrue(passed["observations_redacted"])
        for invalid in ["https://example.org/test/data","http://127.0.0.1:9999/admin",
                        "http://127.0.0.1:9999/test/data?patient=x",
                        "http://localhost:9999/test/data"]:
            with self.subTest(url=invalid),self.assertRaises(ValueError):
                check_local_json(invalid,"status","ok",authorized=True)

    def test_stored_links_are_requirement_to_execution_to_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            db=Workspace(Path(directory)/"test.db")
            try:
                system=db.add_system("Synthetic LIS","Demonstration","Author")
                spec=json.loads(PROTOCOL.read_text())
                spec["system"]["id"]=system["id"]
                draft=db.draft_protocol(system["id"],spec,"Author")
                db.baseline(draft["id"],"Reviewer","Synthetic engineering baseline")
                run=db.execute(draft["id"],"Author")
                results=run["results"]
                self.assertEqual(results["run_id"],run["id"])
                self.assertEqual(results["protocol_digest"],draft["digest"])
                for test in results["results"]:
                    self.assertEqual(test["evidence_ref"],f'hq-run:{run["id"]}/test/{test["id"]}')
                    self.assertEqual(test["actual"],"[WITHHELD]")
                for row in results["traceability"]:
                    refs=[t["evidence_ref"] for t in results["results"] if t["id"] in row["test_ids"]]
                    self.assertEqual(row["evidence_refs"],refs)
            finally:
                db.close()

    def test_restore_verified_rejects_tamper_and_existing_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            original=Path(directory)/"original.db"
            con=sqlite3.connect(original)
            con.execute("CREATE TABLE t(id INTEGER PRIMARY KEY, value TEXT)")
            con.execute("INSERT INTO t(value) VALUES('synthetic')")
            con.commit()
            backup=Path(directory)/"backup.db"
            manifest=backup_sqlite(original,backup)
            target=Path(directory)/"restore.db"
            result=restore_verified(backup,target,manifest["sha256"])
            self.assertTrue(result["restored"])
            self.assertFalse(result["regulated_recovery_verified"])
            recovered=sqlite3.connect(target)
            self.assertEqual(recovered.execute("SELECT value FROM t").fetchone()[0],"synthetic")
            recovered.close()
            with self.assertRaises(ValueError):
                restore_verified(backup,target,manifest["sha256"])
            with self.assertRaises(ValueError):
                restore_verified(backup,Path(directory)/"other.db","0"*64)
            con.close()

if __name__=="__main__":
    unittest.main()
