"""Plain pytest baseline on the identical supplied protocol and fixtures.

Failure is expected for the five deliberately seeded synthetic defects.
"""
import json
import os
from pathlib import Path
import pytest
from benchmarks.independent_baseline import baseline_observe

DATA=json.loads(Path(os.environ.get(
    "HQ_BENCH_PROTOCOL","examples/synthetic_lis_v2/protocol.json")).read_text(encoding="utf-8"))
@pytest.mark.parametrize("case",DATA["tests"],ids=lambda x:x["id"])
def test_synthetic_requirement(case):
    assert case["fixture"] in DATA["fixtures"],"NOT_RUN: fixture missing"
    assert baseline_observe(case["check"],DATA["fixtures"][case["fixture"]],case)
