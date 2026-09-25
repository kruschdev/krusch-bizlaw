"""
tests/test_benchmark_gate.py
============================
Pytest gate verifying 100.0% convergence across all 11 Contract-vs-Statute Join benchmark scenarios.
"""

from scripts.eval_benchmark import BENCHMARK_SCENARIOS
from src.engine.join import evaluate_contract_vs_statute_slots


def test_all_11_benchmark_scenarios_pass():
    passed = 0
    total = len(BENCHMARK_SCENARIOS)

    for tc in BENCHMARK_SCENARIOS:
        finding = evaluate_contract_vs_statute_slots(
            topic=tc["topic"],
            as_of=tc["as_of_date"],
            contract_slots=tc["contract_slots"],
            contract_clause_info=tc["clause_info"],
            property_type=tc["property_type"]
        )
        assert finding.alignment == tc["expected_alignment"], (
            f"Scenario {tc['id']} alignment mismatch: got {finding.alignment}, expected {tc['expected_alignment']}"
        )
        assert finding.enforceability == tc["expected_enforceability"], (
            f"Scenario {tc['id']} enforceability mismatch: got {finding.enforceability}, expected {tc['expected_enforceability']}"
        )
        passed += 1

    assert passed == total == 11
