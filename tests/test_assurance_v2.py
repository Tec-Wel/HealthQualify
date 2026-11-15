"""Pre-alpha v0.2 healthcare qualification contract and safety tests."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from healthqualify.assurance import assess_v2, save_v2, validate_v2, verify_v2, digest
from healthqualify.healthcare import parse_hl7

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "synthetic_lis_v2" / "protocol.json"


class AssuranceV2Tests(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_five_seeded_healthcare_failures(self):
        results = assess_v2(self.doc)
        self.assertEqual(results["summary"], {"PASS": 2, "FAIL": 5, "ERROR": 0, "NOT_RUN": 0})
        self.assertEqual(len(results["gaps"]), 5)
        self.assertFalse(results["qualification_approved"])
        self.assertTrue(all(x["acceptance_basis"] for x in results["traceability"]))

    def test_missing_acceptance_basis_rejected(self):
        del self.doc["requirements"][0]["acceptance_basis"]
        with self.assertRaises(ValueError):
            validate_v2(self.doc)

    def test_invented_expected_value_rejected(self):
        del self.doc["tests"][0]["expected"]
        with self.assertRaises(ValueError):
            validate_v2(self.doc)

    def test_cross_requirement_link_rejected(self):
        self.doc["tests"][0]["requirement_ids"] = ["URS-999"]
        with self.assertRaises(ValueError):
            validate_v2(self.doc)

    def test_no_undeclared_approval(self):
        self.doc["qualification_state"] = "approved"
        with self.assertRaises(ValueError):
            validate_v2(self.doc)

    def test_reject_unsupported_or_executable_checks(self):
        self.doc["tests"][0]["check"] = "run_shell_command"
        with self.assertRaises(ValueError):
            validate_v2(self.doc)

    def test_missing_fixture_is_not_run_not_pass(self):
        del self.doc["fixtures"]["fhir_observation"]
        result = assess_v2(self.doc)
        self.assertEqual(result["summary"]["NOT_RUN"], 1)
        self.assertIn("NOT_RUN", {g["kind"] for g in result["gaps"]})

    def test_invalid_hl7_is_error_not_pass(self):
        self.doc["fixtures"]["hl7_oru"] = "not an HL7 message"
        result = assess_v2(self.doc)
        self.assertEqual(result["summary"]["ERROR"], 2)
        self.assertEqual(result["summary"]["PASS"], 2)

    def test_detect_uncovered_requirement(self):
        self.doc["requirements"].append({
            "id": "URS-008", "risk": "high", "acceptance_basis": "Synthetic requirement without mapped test"
        })
        result = assess_v2(self.doc)
        self.assertEqual(result["traceability"][-1]["status"], "NOT_RUN")
        self.assertEqual(result["gaps"][-1]["kind"], "FAIL")
        self.assertTrue(any(g.get("kind") == "UNCOVERED" for g in result["gaps"]))

    def test_manifest_and_tamper(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "run"
            save_v2(EXAMPLE.read_bytes(), out)
            trusted = digest((out / "manifest.json").read_bytes())
            self.assertTrue(verify_v2(out, trusted))
            self.assertFalse(verify_v2(out, "0" * 64))
            (out / "results.json").write_text("{}", encoding="utf-8")
            self.assertFalse(verify_v2(out, trusted))

    def test_hl7_parser_works_with_cr_and_lf(self):
        message = self.doc["fixtures"]["hl7_oru"]
        parsed = parse_hl7(message)
        self.assertEqual(parsed["PID"][0][3], "P999^^^HOSP^MR")


if __name__ == "__main__":
    unittest.main()
