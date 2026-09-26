#!/usr/bin/env python3
"""
scripts/eval_benchmark.py
=========================
1-Command Cross-Engine Compliance Evaluation Benchmark for KruschBizLaw.
Evaluates 11 end-to-end conflict test pairs comparing commercial and residential
contract slots against statutory ceilings, floors, and non-waivable doctrines.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import date, datetime, timezone
from typing import Any, Dict

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.engine.join import evaluate_contract_vs_statute_slots
from src.engine.models import AlignmentVerdict, EnforceabilityVerdict

# ANSI Styling
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


BENCHMARK_SCENARIOS = [
    {
        "id": "TC-01",
        "name": "Post-AB 12 Security Deposit Violation (2.0 mo demanded post-2024-07-01)",
        "topic": "SECURITY_DEPOSIT",
        "as_of_date": date(2024, 8, 1),
        "property_type": "residential",
        "contract_slots": {"deposit_cap_months": 2.0},
        "clause_info": {
            "instrument": "Residential Lease 2024",
            "section": "Sec 3.1",
            "span": "Tenant shall deposit an amount equal to two (2) months rent ($5,000) as security.",
            "normalized_slot": {"deposit_cap_months": 2.0}
        },
        "expected_alignment": AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value,
        "expected_enforceability": EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value,
        "governing_statute": "Cal. Civ. Code § 1950.5(c)(1)",
    },
    {
        "id": "TC-02",
        "name": "Pre-AB 12 Security Deposit Compliance (2.0 mo demanded pre-2024-07-01)",
        "topic": "SECURITY_DEPOSIT",
        "as_of_date": date(2024, 3, 1),
        "property_type": "residential",
        "contract_slots": {"deposit_cap_months": 2.0},
        "clause_info": {
            "instrument": "Residential Lease Pre-2024",
            "section": "Sec 3.1",
            "span": "Tenant shall provide security deposit of 2.0 months unfurnished rent.",
            "normalized_slot": {"deposit_cap_months": 2.0}
        },
        "expected_alignment": AlignmentVerdict.ALIGNED.value,
        "expected_enforceability": EnforceabilityVerdict.ENFORCEABLE.value,
        "governing_statute": "Cal. Civ. Code § 1950.5(c) (Prior to AB 12)",
    },
    {
        "id": "TC-03",
        "name": "Sub-Statutory Landlord Entry Notice (12 hrs vs 24 hr § 1954 floor)",
        "topic": "ENTRY_NOTICE",
        "as_of_date": date(2024, 8, 1),
        "property_type": "residential",
        "contract_slots": {"entry_notice_hours": 12.0},
        "clause_info": {
            "instrument": "Residential Lease 2024",
            "section": "Sec 8.2",
            "span": "Landlord may enter premises upon twelve (12) hours advance verbal or written notice.",
            "normalized_slot": {"entry_notice_hours": 12.0}
        },
        "expected_alignment": AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value,
        "expected_enforceability": EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value,
        "governing_statute": "Cal. Civ. Code § 1954(d)(1)",
    },
    {
        "id": "TC-04",
        "name": "More Generous Landlord Entry Notice (48 hrs vs 24 hr § 1954 floor)",
        "topic": "ENTRY_NOTICE",
        "as_of_date": date(2024, 8, 1),
        "property_type": "residential",
        "contract_slots": {"entry_notice_hours": 48.0},
        "clause_info": {
            "instrument": "Tenant-Favorable Lease",
            "section": "Sec 7.1",
            "span": "Landlord covenants to provide at least 48 hours written notice prior to entering.",
            "normalized_slot": {"entry_notice_hours": 48.0}
        },
        "expected_alignment": AlignmentVerdict.CONTRACT_MORE_GENEROUS.value,
        "expected_enforceability": EnforceabilityVerdict.ENFORCEABLE.value,
        "governing_statute": "Cal. Civ. Code § 1954(d)(1)",
    },
    {
        "id": "TC-05",
        "name": "Extended Security Deposit Return Timeline (45 days vs 21-day ceiling)",
        "topic": "DEPOSIT_RETURN",
        "as_of_date": date(2024, 8, 1),
        "property_type": "residential",
        "contract_slots": {"deposit_return_days": 45.0},
        "clause_info": {
            "instrument": "Residential Lease 2024",
            "section": "Sec 3.4",
            "span": "Landlord shall have forty-five (45) calendar days after surrender to return unused deposit.",
            "normalized_slot": {"deposit_return_days": 45.0}
        },
        "expected_alignment": AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value,
        "expected_enforceability": EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value,
        "governing_statute": "Cal. Civ. Code § 1950.5(g)(1)",
    },
    {
        "id": "TC-06",
        "name": "Expedited Security Deposit Return Timeline (14 days vs 21-day ceiling)",
        "topic": "DEPOSIT_RETURN",
        "as_of_date": date(2024, 8, 1),
        "property_type": "residential",
        "contract_slots": {"deposit_return_days": 14.0},
        "clause_info": {
            "instrument": "Premium Lease",
            "section": "Sec 4.0",
            "span": "Security deposit statement and return shall be furnished within 14 calendar days.",
            "normalized_slot": {"deposit_return_days": 14.0}
        },
        "expected_alignment": AlignmentVerdict.CONTRACT_MORE_GENEROUS.value,
        "expected_enforceability": EnforceabilityVerdict.ENFORCEABLE.value,
        "governing_statute": "Cal. Civ. Code § 1950.5(g)(1)",
    },
    {
        "id": "TC-07",
        "name": "Prohibited Habitability & Repair-and-Deduct Waiver (§ 1942.1)",
        "topic": "HABITABILITY_WAIVER",
        "as_of_date": date(2024, 8, 1),
        "property_type": "residential",
        "contract_slots": {"waives_habitability": True, "waives_repair_deduct": True},
        "clause_info": {
            "instrument": "Residential Lease 2024",
            "section": "Sec 14.1",
            "span": "Tenant accepts premises strictly as-is and waives all statutory rights under Section 1941 and 1942 to repair and deduct.",
            "normalized_slot": {"waives_habitability": True, "waives_repair_deduct": True}
        },
        "expected_alignment": AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value,
        "expected_enforceability": EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value,
        "governing_statute": "Cal. Civ. Code § 1942.1",
    },
    {
        "id": "TC-08",
        "name": "Prohibited Retaliation Defense Waiver (§ 1942.5(h))",
        "topic": "RETALIATION_WAIVER",
        "as_of_date": date(2024, 8, 1),
        "property_type": "residential",
        "contract_slots": {"waives_retaliation_defense": True},
        "clause_info": {
            "instrument": "Residential Lease 2024",
            "section": "Sec 19.3",
            "span": "Tenant covenants that it waives any right to assert retaliatory eviction defenses under Section 1942.5.",
            "normalized_slot": {"waives_retaliation_defense": True}
        },
        "expected_alignment": AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value,
        "expected_enforceability": EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value,
        "governing_statute": "Cal. Civ. Code § 1942.5(h)",
    },
    {
        "id": "TC-09",
        "name": "Excessive Late Payment Fee / Liquidated Damages (15% vs 5% § 1671(d) ceiling)",
        "topic": "LATE_FEE",
        "as_of_date": date(2024, 8, 1),
        "property_type": "residential",
        "contract_slots": {"late_penalty_pct": 15.0},
        "clause_info": {
            "instrument": "Residential Lease 2024",
            "section": "Sec 4.2",
            "span": "A late fee of fifteen percent (15%) shall be assessed for any rent paid after the 3rd.",
            "normalized_slot": {"late_penalty_pct": 15.0}
        },
        "expected_alignment": AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value,
        "expected_enforceability": EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value,
        "governing_statute": "Cal. Civ. Code § 1671(d)",
    },
    {
        "id": "TC-10",
        "name": "Commercial Lease Security Deposit Freedom of Contract (§ 1950.7(f) flexibility)",
        "topic": "COMMERCIAL_SECURITY_DEPOSIT",
        "as_of_date": date(2024, 8, 1),
        "property_type": "commercial",
        "contract_slots": {"deposit_cap_months": 3.0},
        "clause_info": {
            "instrument": "Commercial Industrial Lease",
            "section": "Sec 5.1",
            "span": "Tenant shall maintain security deposit equal to 3.0 months base rent.",
            "normalized_slot": {"deposit_cap_months": 3.0}
        },
        "expected_alignment": AlignmentVerdict.ALIGNED.value,
        "expected_enforceability": EnforceabilityVerdict.ENFORCEABLE.value,
        "governing_statute": "Cal. Civ. Code § 1950.7(f)",
    },
    {
        "id": "TC-11",
        "name": "Untracked Topic Coverage Gap Detection (Unknown topic -> COVERAGE_GAP)",
        "topic": "MUNICIPAL_SIDEWALK",
        "as_of_date": date(2024, 8, 1),
        "property_type": "residential",
        "contract_slots": {},
        "clause_info": None,
        "expected_alignment": AlignmentVerdict.COVERAGE_GAP.value,
        "expected_enforceability": EnforceabilityVerdict.UNSPECIFIED.value,
        "governing_statute": None,
    }
]


def run_benchmark() -> Dict[str, Any]:
    print(f"\n{BOLD}{CYAN}{'=' * 90}{RESET}")
    print(f"{BOLD}{CYAN}⚖️  KRUSCH-BIZLAW: CROSS-DOMAIN STATUTORY COMPLIANCE BENCHMARK{RESET}")
    print(f"{DIM}Evaluating 11 Contract-vs-Statute Join scenarios under historical as-of dates{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 90}{RESET}\n")

    passed_count = 0
    total_count = len(BENCHMARK_SCENARIOS)
    results = []

    start_time = time.perf_counter()

    for idx, tc in enumerate(BENCHMARK_SCENARIOS, 1):
        t0 = time.perf_counter()
        finding = evaluate_contract_vs_statute_slots(
            topic=tc["topic"],
            as_of=tc["as_of_date"],
            contract_slots=tc["contract_slots"],
            contract_clause_info=tc["clause_info"],
            property_type=tc["property_type"]
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        align_pass = finding.alignment == tc["expected_alignment"]
        enforce_pass = finding.enforceability == tc["expected_enforceability"]
        is_pass = align_pass and enforce_pass

        if is_pass:
            passed_count += 1
            status_badge = f"{GREEN}✓ PASS{RESET}"
        else:
            status_badge = f"{RED}✗ FAIL{RESET}"

        print(f"[{idx:02d}/{total_count:02d}] {tc['id']}: {tc['name']}")
        print(f"     Status: {status_badge} ({elapsed_ms:.2f}ms)")
        print(f"     Alignment:      {finding.alignment} (Expected: {tc['expected_alignment']})")
        print(f"     Enforceability: {finding.enforceability} (Expected: {tc['expected_enforceability']})")
        print(f"     Explanation:    {DIM}{finding.explanation}{RESET}\n")

        results.append({
            "id": tc["id"],
            "name": tc["name"],
            "passed": is_pass,
            "measured_alignment": finding.alignment,
            "expected_alignment": tc["expected_alignment"],
            "measured_enforceability": finding.enforceability,
            "expected_enforceability": tc["expected_enforceability"],
            "latency_ms": elapsed_ms
        })

    total_time_ms = (time.perf_counter() - start_time) * 1000.0
    pass_rate = (passed_count / total_count) * 100.0

    print(f"{BOLD}{CYAN}{'=' * 90}{RESET}")
    print(f"{BOLD}BENCHMARK SUMMARY:{RESET}")
    print(f"  Total Scenarios: {total_count}")
    print(f"  Passed:          {GREEN if passed_count == total_count else RED}{passed_count}/{total_count} ({pass_rate:.1f}%){RESET}")
    print(f"  Total Execution: {total_time_ms:.2f} ms ({total_time_ms / total_count:.2f} ms/join)")
    print(f"{BOLD}{CYAN}{'=' * 90}{RESET}\n")

    summary_data = {
        "benchmark": "krusch-bizlaw-contract-vs-statute",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_scenarios": total_count,
        "passed": passed_count,
        "pass_rate_pct": pass_rate,
        "total_latency_ms": total_time_ms,
        "results": results
    }

    # Save results to data/eval
    os.makedirs(os.path.join(PROJECT_ROOT, "data", "eval"), exist_ok=True)
    out_path = os.path.join(PROJECT_ROOT, "data", "eval", "benchmark_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    return summary_data


if __name__ == "__main__":
    data = run_benchmark()
    if data["passed"] != data["total_scenarios"]:
        sys.exit(1)
    sys.exit(0)
