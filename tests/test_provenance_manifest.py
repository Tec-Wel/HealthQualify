"""Technical manifest checks; never infer third-party rights from byte hashes."""
from __future__ import annotations

import importlib.util
import re
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "create_provenance_manifest.py"


class ProvenanceManifestTests(unittest.TestCase):
    def test_local_manifest_has_nonclearance_and_sha256_fields(self):
        spec = importlib.util.spec_from_file_location("hq_provenance_manifest", SCRIPT)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        self.assertIsNotNone(spec.loader)
        spec.loader.exec_module(module)
        manifest = module.build_manifest()
        self.assertFalse(manifest["rights_verified"])
        self.assertEqual(manifest["legal_clearance"], "NOT_GRANTED")
        self.assertTrue(manifest["records"])
        self.assertEqual(
            [row["path"] for row in manifest["records"]],
            sorted(row["path"] for row in manifest["records"]),
        )
        for row in manifest["records"]:
            self.assertRegex(row["sha256"], r"^[0-9a-f]{64}$")
            self.assertGreaterEqual(row["bytes"], 0)
            self.assertIn(row["category"], {"visual-asset", "dependency-or-license-declaration"})


if __name__ == "__main__":
    unittest.main()
