"""Additional safety checks for report integrity and regulatory change receipts."""
import tempfile
import unittest
from pathlib import Path

from healthqualify.evidence import seal_export,verify_seal
from healthqualify.regwatch import RegulationWatch

class EvidenceAndWatchTests(unittest.TestCase):
    def test_receipt_requires_externally_held_secret_and_detects_tampering(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/"manifest.json").write_text('{"files":{}}',encoding="utf-8")
            secret=b"s"*32
            with self.assertRaises(ValueError):
                seal_export(root,b"weak")
            receipt=seal_export(root,secret)
            self.assertEqual(receipt["method"],"HMAC-SHA256")
            self.assertTrue(verify_seal(root,secret))
            self.assertFalse(verify_seal(root,b"q"*32))
            (root/"manifest.json").write_text('{"files":{"modified":true}}',encoding="utf-8")
            self.assertFalse(verify_seal(root,secret))

    def test_regulatory_snapshot_diff_is_review_only(self):
        with tempfile.TemporaryDirectory() as temp:
            watch=RegulationWatch(Path(temp)/"regwatch.db")
            try:
                first=watch.capture("us-part-11","synthetic sample paragraph A")
                self.assertTrue(first["review_required"])
                same=watch.capture("us-part-11","synthetic sample paragraph A")
                self.assertFalse(same["changed"])
                changed=watch.capture("us-part-11","synthetic sample paragraph B")
                self.assertTrue(changed["changed"])
                self.assertTrue(changed["diff"]["changed"])
                self.assertTrue(changed["review_required"])
                self.assertIn("not independently",changed["source_claim"])
                with self.assertRaises(ValueError):
                    watch.capture("unknown-framework","anything")
            finally:
                watch.close()

if __name__=="__main__":
    unittest.main()
