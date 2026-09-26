"""
tests/test_invariants.py
========================
Automated pass/fail test suite verifying the 10 Core Architectural Invariants
of KruschBizLaw ("The Join") as specified in docs/INVARIANTS.md.
"""

from __future__ import annotations

from datetime import date
from fastapi.testclient import TestClient

from src.backend.config import is_strict_loopback
from src.backend.clients import KruschBizClient, KruschLawClient
from src.backend.main import app
from src.engine.join import evaluate_contract_vs_statute_slots
from src.engine.models import AlignmentVerdict, EnforceabilityVerdict

client = TestClient(app)


class TestKruschBizLawInvariants:
    """Pass/Fail test matrix for INV-1 through INV-10."""

    def test_inv_01_mandatory_as_of_date(self):
        """INV-1: Mandatory As-Of Date. Missing, empty, or whitespace dates must be rejected."""
        # Missing field
        res1 = client.post("/api/conflicts/contract-vs-statute", json={"jurisdiction": "CA:Oakland", "topics": ["SECURITY_DEPOSIT"]})
        assert res1.status_code == 422 or res1.status_code == 400

        # Empty string
        res2 = client.post("/api/conflicts/contract-vs-statute", json={"as_of_date": "", "jurisdiction": "CA:Oakland", "topics": ["SECURITY_DEPOSIT"]})
        assert res2.status_code == 400
        assert "as_of_date" in res2.json()["detail"].lower()

        # Whitespace
        res3 = client.post("/api/conflicts/contract-vs-statute", json={"as_of_date": "   ", "jurisdiction": "CA:Oakland", "topics": ["SECURITY_DEPOSIT"]})
        assert res3.status_code == 400

        # Invalid format
        res4 = client.post("/api/conflicts/contract-vs-statute", json={"as_of_date": "08-15-2024", "jurisdiction": "CA:Oakland", "topics": ["SECURITY_DEPOSIT"]})
        assert res4.status_code == 400
        assert "format" in res4.json()["detail"].lower()

    def test_inv_02_deterministic_slot_evaluation(self):
        """INV-2: Deterministic Slot Evaluation. Boundary values must evaluate via typed arithmetic."""
        # Exactly at 1.0 month ceiling -> ALIGNED
        f_exact = evaluate_contract_vs_statute_slots(
            topic="SECURITY_DEPOSIT",
            as_of=date(2024, 8, 1),
            contract_slots={"deposit_cap_months": 1.0},
            property_type="residential"
        )
        assert f_exact.alignment == AlignmentVerdict.ALIGNED.value
        assert f_exact.enforceability == EnforceabilityVerdict.ENFORCEABLE.value

        # Slightly over 1.001 month ceiling -> VOID
        f_over = evaluate_contract_vs_statute_slots(
            topic="SECURITY_DEPOSIT",
            as_of=date(2024, 8, 1),
            contract_slots={"deposit_cap_months": 1.001},
            property_type="residential"
        )
        assert f_over.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
        assert f_over.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value

    def test_inv_03_ab12_temporal_boundary_gating(self):
        """INV-3: AB 12 Temporal Boundary Gating. Boundary split on July 1, 2024."""
        # Pre-AB 12: June 30, 2024 -> 2.0 months is compliant
        f_pre = evaluate_contract_vs_statute_slots(
            topic="SECURITY_DEPOSIT",
            as_of=date(2024, 6, 30),
            contract_slots={"deposit_cap_months": 2.0},
            property_type="residential"
        )
        assert f_pre.alignment == AlignmentVerdict.ALIGNED.value
        assert f_pre.enforceability == EnforceabilityVerdict.ENFORCEABLE.value
        assert "Prior to AB 12" in f_pre.controlling_statute["citation"]

        # Post-AB 12: July 1, 2024 -> 2.0 months is VOID
        f_post = evaluate_contract_vs_statute_slots(
            topic="SECURITY_DEPOSIT",
            as_of=date(2024, 7, 1),
            contract_slots={"deposit_cap_months": 2.0},
            property_type="residential"
        )
        assert f_post.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
        assert f_post.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value
        assert "AB 12" in f_post.controlling_statute["span"]

    def test_inv_04_commercial_lease_freedom_of_contract(self):
        """INV-4: Commercial Lease Freedom of Contract. § 1950.7(f) permissive waiver."""
        f_comm = evaluate_contract_vs_statute_slots(
            topic="SECURITY_DEPOSIT",
            as_of=date(2024, 8, 1),
            contract_slots={"deposit_cap_months": 3.0},
            property_type="commercial"
        )
        assert f_comm.alignment == AlignmentVerdict.ALIGNED.value
        assert f_comm.enforceability == EnforceabilityVerdict.ENFORCEABLE.value
        assert "1950.7" in f_comm.controlling_statute["citation"]
        assert f_comm.controlling_statute["mandate_type"] == "STATUTORY_PERMISSIVE_WAIVER"

    def test_inv_05_non_waivable_public_policy_void_gating(self):
        """INV-5: Non-Waivable Public Policy Prohibition Gating."""
        # Habitability disclaimer
        f_hab = evaluate_contract_vs_statute_slots(
            topic="HABITABILITY_WAIVER",
            as_of=date(2024, 8, 1),
            contract_slots={"waives_habitability": True}
        )
        assert f_hab.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
        assert f_hab.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value
        assert "1942.1" in f_hab.controlling_statute["citation"]

        # Retaliation disclaimer
        f_ret = evaluate_contract_vs_statute_slots(
            topic="RETALIATION_WAIVER",
            as_of=date(2024, 8, 1),
            contract_slots={"waives_retaliation_defense": True}
        )
        assert f_ret.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
        assert f_ret.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value
        assert "1942.5(h)" in f_ret.controlling_statute["citation"]

    def test_inv_06_fail_closed_coverage_hole_handling(self):
        """INV-6: Fail-Closed Coverage Hole Handling. Unmapped topic returns coverage_gap."""
        f_gap = evaluate_contract_vs_statute_slots(
            topic="UNMAPPED_LOCAL_ORDINANCE",
            as_of=date(2024, 8, 1),
            contract_slots={"some_slot": 123}
        )
        assert f_gap.alignment == AlignmentVerdict.COVERAGE_GAP.value
        assert f_gap.enforceability == EnforceabilityVerdict.UNSPECIFIED.value
        assert f_gap.controlling_statute is None

    def test_inv_07_generous_term_recognition(self):
        """INV-7: Generous Term Recognition. Floors vs Ceilings."""
        # Exceeding statutory floor (Entry notice: 48h vs 24h floor) -> MORE_GENEROUS & ENFORCEABLE
        f_floor = evaluate_contract_vs_statute_slots(
            topic="ENTRY_NOTICE",
            as_of=date(2024, 8, 1),
            contract_slots={"entry_notice_hours": 48.0}
        )
        assert f_floor.alignment == AlignmentVerdict.CONTRACT_MORE_GENEROUS.value
        assert f_floor.enforceability == EnforceabilityVerdict.ENFORCEABLE.value

        # Exceeding statutory ceiling (Return days: 30d vs 21d ceiling) -> LESS_THAN_MANDATORY & VOID
        f_ceil = evaluate_contract_vs_statute_slots(
            topic="DEPOSIT_RETURN",
            as_of=date(2024, 8, 1),
            contract_slots={"deposit_return_days": 30.0}
        )
        assert f_ceil.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
        assert f_ceil.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value

    def test_inv_08_strict_loopback_data_residency(self):
        """INV-8: Strict Loopback Data Residency verification."""
        assert is_strict_loopback("127.0.0.1") is True
        assert is_strict_loopback("localhost") is True
        assert is_strict_loopback("::1") is True
        assert is_strict_loopback("0.0.0.0") is False
        assert is_strict_loopback("10.0.0.44") is False
        assert is_strict_loopback("http://192.168.1.100:8087") is False

    def test_inv_09_resilient_air_gapped_fleet_federation(self):
        """INV-9: Resilient Air-Gapped Fleet Federation. Client adapters gracefully fall back."""
        # Connect to a guaranteed-offline port
        dummy_biz = KruschBizClient(base_url="http://127.0.0.1:59999", timeout=0.1)
        dummy_law = KruschLawClient(base_url="http://127.0.0.1:59999", timeout=0.1)

        assert dummy_biz.check_health() is False
        assert dummy_law.check_health() is False

        # Query methods must return None, not raise unhandled exceptions
        assert dummy_biz.get_controlling_clause(counterparty="Test Corp", topic="SECURITY_DEPOSIT", as_of_date="2024-08-01") is None
        assert dummy_law.get_controlling_law(doctrine="Security Deposit", as_of_date="2024-08-01") is None

    def test_inv_10_trace_and_audit_immutability(self):
        """INV-10: Trace & Audit Immutability. Unique, validated trace_id generated for every finding."""
        f1 = evaluate_contract_vs_statute_slots(
            topic="SECURITY_DEPOSIT",
            as_of=date(2024, 8, 1),
            contract_slots={"deposit_cap_months": 1.0}
        )
        f2 = evaluate_contract_vs_statute_slots(
            topic="SECURITY_DEPOSIT",
            as_of=date(2024, 8, 1),
            contract_slots={"deposit_cap_months": 1.0}
        )

        assert f1.trace_id.startswith("trace_bizlaw_")
        assert f2.trace_id.startswith("trace_bizlaw_")
        assert f1.trace_id != f2.trace_id
        assert f1.coverage == "partial"
