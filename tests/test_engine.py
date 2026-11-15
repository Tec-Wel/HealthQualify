import json
import tempfile
import unittest
from pathlib import Path

from healthqualify.engine import execute, save_run, verify_run


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "examples" / "synthetic_lis" / "protocol.json"


class EngineTests(unittest.TestCase):
    def load_demo(self):
        return json.loads(DEMO.read_text(encoding="utf-8"))

    def test_detects_seeded_failures(self):
        report = execute(self.load_demo())
        self.assertEqual(report["summary"]["FAIL"], 2)
        self.assertEqual(report["summary"]["PASS"], 4)
        self.assertFalse(report["qualification_approved"])

    def test_no_missing_fixture_is_passed(self):
        protocol = self.load_demo()
        del protocol["fixtures"]["critical_notification"]
        result = execute(protocol)
        self.assertIn("NOT_RUN", [x["status"] for x in result["results"]])
        self.assertNotEqual(result["summary"]["NOT_RUN"], 0)

    def test_rejects_unknown_check(self):
        protocol = self.load_demo()
        protocol["tests"][0]["check"] = "shell"
        with self.assertRaises(ValueError):
            execute(protocol)

    def test_export_integrity(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "run"
            save_run(DEMO.read_bytes(), out)
            self.assertTrue(verify_run(out))
            (out / "results.json").write_text("{}")
            self.assertFalse(verify_run(out))


if __name__ == "__main__":
    unittest.main()
