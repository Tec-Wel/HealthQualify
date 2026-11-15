"""Offline tests for GitHub change-impact planning."""
import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch
from healthqualify.ci_impact import analyze

SHA="a"*40
DEMO="examples/synthetic_lis_v3/protocol.json"

class ImpactCITests(unittest.TestCase):
    @patch("healthqualify.ci_impact.subprocess.run")
    def test_mapped_code_change(self,mock_run):
        mock_run.return_value=subprocess.CompletedProcess([],0,"healthqualify/healthcare.py\n","")
        result=analyze(SHA,DEMO)
        self.assertEqual(result["impact"],"REVIEW_REQUIRED")
        self.assertTrue(result["human_review_required"])
        self.assertFalse(result["qualification_approved"])
        self.assertGreater(len(result["recommended_test_ids"]),0)
        self.assertEqual(mock_run.call_args.args[0][0:3],["git","diff","--name-only"])

    @patch("healthqualify.ci_impact.subprocess.run")
    def test_unmapped_change_is_unknown(self,mock_run):
        mock_run.return_value=subprocess.CompletedProcess([],0,"docs/safety.md\n","")
        result=analyze(SHA,DEMO)
        self.assertEqual(result["impact"],"UNKNOWN_IMPACT")
        self.assertEqual(len(result["recommended_test_ids"]),7)
        self.assertEqual(result["unmapped_paths"],["docs/safety.md"])

    @patch("healthqualify.ci_impact.subprocess.run")
    def test_no_changed_files_never_approves(self,mock_run):
        mock_run.return_value=subprocess.CompletedProcess([],0,"","")
        result=analyze(SHA,DEMO)
        self.assertEqual(result["impact"],"NO_CHANGED_FILES")
        self.assertFalse(result["qualification_approved"])
        self.assertTrue(result["human_review_required"])

    def test_invalid_base_sha_fails_closed(self):
        with self.assertRaises(ValueError):
            analyze("HEAD; echo unsafe",DEMO)

if __name__=="__main__":
    unittest.main()
