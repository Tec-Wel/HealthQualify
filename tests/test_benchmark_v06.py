"""Equal-input synthetic benchmark regression checks."""
import unittest
from benchmarks.compare import benchmark
from benchmarks.independent_baseline import execute_baseline,traceability_baseline

class ComparisonTests(unittest.TestCase):
    def test_independent_execution_and_traceability(self):
        import json
        from pathlib import Path
        doc=json.loads((Path(__file__).resolve().parents[1]/
                        "examples/synthetic_lis_v2/protocol.json").read_text())
        results=execute_baseline(doc)
        self.assertEqual(len(results),7)
        self.assertEqual(sum(x["status"]=="FAIL" for x in results),5)
        self.assertEqual(len(traceability_baseline(doc,results)),7)

    def test_three_implementations_identical_seeded_outcomes(self):
        result=benchmark(repetitions=1)
        self.assertEqual(result["known_seeded_defects"],5)
        self.assertEqual(result["setup_effort"],"NOT_MEASURED")
        self.assertFalse(result["claim_of_superiority"])
        for label in ("HealthQualify","Independent stdlib","Plain pytest"):
            item=result["results"][label]
            self.assertEqual(item["status"],"MEASURED")
            self.assertEqual(item["cases"],7)
            self.assertEqual(item["seeded_defects_detected"],5)
            self.assertEqual(item["pass"],2)
            self.assertGreaterEqual(item["median_runtime_ms"],0)

if __name__=="__main__":
    unittest.main()
