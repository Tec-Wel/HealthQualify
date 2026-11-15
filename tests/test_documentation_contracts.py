"""Documentation contracts: local relative links and a runnable template fixture."""
import json
import re
import unittest
from pathlib import Path

from healthqualify.protocol_v3 import validate_v3, execute_v3

ROOT = Path(__file__).resolve().parents[1]
GUIDES = [
    "docs/API_REFERENCE.md", "docs/DEVELOPER_ARCHITECTURE.md",
    "docs/CUSTOM_ADAPTER_GUIDE.md", "docs/TESTING_AND_CI.md",
    "docs/HEALTHCARE_USE_CASES.md", "docs/QUALIFICATION_METHODOLOGY.md",
    "docs/REGULATORY_MAPPING.md", "docs/VALIDATION_TEMPLATES.md",
    "docs/DEPLOYMENT_GUIDE.md", "docs/OPERATIONS_RUNBOOK.md",
    "docs/SECURITY_MODEL.md", "docs/PRODUCTION_READINESS_CHECKLIST.md",
    "docs/EVALUATION_GUIDE.md", "docs/MIGRATION_GUIDE.md",
    "docs/FAQ.md", "docs/FEATURE_MATRIX.md", "docs/DOCUMENTATION_INDEX.md",
    "docs/VERSIONING_POLICY.md", "README.md", "SECURITY.md",
    "SUPPORT.md", "CHANGELOG.md",
]
PATTERN = re.compile(r"!?\[[^\]]+\]\(([^)]+)\)")


class DocumentationContracts(unittest.TestCase):
    def test_local_links_exist(self):
        for filename in sorted(set(GUIDES + [str(p.relative_to(ROOT)) for p in (ROOT / "docs").glob("*.md")])):
            path = ROOT / filename
            self.assertTrue(path.is_file(), filename)
            for target in PATTERN.findall(path.read_text(encoding="utf-8")):
                url = target.split("#", 1)[0]
                if not url or "://" in url or url.startswith("mailto:"):
                    continue
                with self.subTest(source=filename, target=url):
                    resolved = (path.parent / url).resolve()
                    self.assertTrue(resolved.is_relative_to(ROOT.resolve()), "Link escapes repository")
                    self.assertTrue(resolved.exists(), f"Broken local link: {filename} -> {url}")

    def test_synthetic_template_is_executable(self):
        path = ROOT / "examples/templates/strict-synthetic-protocol.json"
        spec = json.loads(path.read_text(encoding="utf-8"))
        validate_v3(spec)
        result = execute_v3(spec)
        self.assertEqual(result["summary"]["PASS"], 1)
        self.assertEqual(result["summary"]["FAIL"], 0)
        self.assertIs(result["qualification_approved"], False)


if __name__ == "__main__":
    unittest.main()
