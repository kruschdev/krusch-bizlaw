"""
tests/test_join_engine.py
=========================
Unit tests for KruschBizLaw deterministic join evaluation engine.
"""

from datetime import date
from src.engine.join import evaluate_contract_vs_statute_slots, synthesize_portfolio_response
from src.engine.models import AlignmentVerdict, EnforceabilityVerdict


def test_ab12_post_enactment_violation():
    """Security deposit of 2.0 months post July 1, 2024 is void under AB 12."""
    finding = evaluate_contract_vs_statute_slots(
        topic="SECURITY_DEPOSIT",
        as_of=date(2024, 8, 1),
        contract_slots={"deposit_cap_months": 2.0},
        property_type="residential"
    )
    assert finding.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
    assert finding.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value
    assert "AB 12" in finding.controlling_statute["span"]


def test_ab12_pre_enactment_compliance():
    """Security deposit of 2.0 months prior to July 1, 2024 is enforceable under prior law."""
    finding = evaluate_contract_vs_statute_slots(
        topic="SECURITY_DEPOSIT",
        as_of=date(2024, 3, 1),
        contract_slots={"deposit_cap_months": 2.0},
        property_type="residential"
    )
    assert finding.alignment == AlignmentVerdict.ALIGNED.value
    assert finding.enforceability == EnforceabilityVerdict.ENFORCEABLE.value


def test_entry_notice_sub_statutory():
    """12 hours notice violates the 24-hour statutory floor under § 1954."""
    finding = evaluate_contract_vs_statute_slots(
        topic="ENTRY_NOTICE",
        as_of=date(2024, 8, 1),
        contract_slots={"entry_notice_hours": 12.0}
    )
    assert finding.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
    assert finding.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value


def test_entry_notice_more_generous():
    """48 hours notice exceeds the 24-hour statutory floor."""
    finding = evaluate_contract_vs_statute_slots(
        topic="ENTRY_NOTICE",
        as_of=date(2024, 8, 1),
        contract_slots={"entry_notice_hours": 48.0}
    )
    assert finding.alignment == AlignmentVerdict.CONTRACT_MORE_GENEROUS.value
    assert finding.enforceability == EnforceabilityVerdict.ENFORCEABLE.value


def test_deposit_return_timeline_violation():
    """45 days return timeline exceeds the 21-day ceiling under § 1950.5(g)(1)."""
    finding = evaluate_contract_vs_statute_slots(
        topic="DEPOSIT_RETURN",
        as_of=date(2024, 8, 1),
        contract_slots={"deposit_return_days": 45.0}
    )
    assert finding.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
    assert finding.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value


def test_habitability_waiver_void():
    """Waiving repair and deduct or habitability is void as against public policy under § 1942.1."""
    finding = evaluate_contract_vs_statute_slots(
        topic="HABITABILITY_WAIVER",
        as_of=date(2024, 8, 1),
        contract_slots={"waives_habitability": True}
    )
    assert finding.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
    assert finding.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value


def test_retaliation_waiver_void():
    """Waiving retaliation defenses is void under § 1942.5(h)."""
    finding = evaluate_contract_vs_statute_slots(
        topic="RETALIATION_WAIVER",
        as_of=date(2024, 8, 1),
        contract_slots={"waives_retaliation_defense": True}
    )
    assert finding.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
    assert finding.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value


def test_commercial_lease_flexibility():
    """Commercial lease deposit waiver applies under § 1950.7(f)."""
    finding = evaluate_contract_vs_statute_slots(
        topic="COMMERCIAL_SECURITY_DEPOSIT",
        as_of=date(2024, 8, 1),
        contract_slots={"deposit_cap_months": 3.0},
        property_type="commercial"
    )
    assert finding.alignment == AlignmentVerdict.ALIGNED.value
    assert finding.enforceability == EnforceabilityVerdict.ENFORCEABLE.value


def test_late_fee_excessive():
    """15% late fee violates the 5% reasonable liquidated damages ceiling under § 1671(d)."""
    finding = evaluate_contract_vs_statute_slots(
        topic="LATE_FEE",
        as_of=date(2024, 8, 1),
        contract_slots={"late_penalty_pct": 15.0}
    )
    assert finding.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
    assert finding.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value


def test_coverage_gap():
    """Unknown topic returns coverage gap."""
    finding = evaluate_contract_vs_statute_slots(
        topic="UNKNOWN_TOPIC_XYZ",
        as_of=date(2024, 8, 1),
        contract_slots={}
    )
    assert finding.alignment == AlignmentVerdict.COVERAGE_GAP.value
    assert finding.enforceability == EnforceabilityVerdict.UNSPECIFIED.value


def test_portfolio_synthesis():
    """Synthesize portfolio response correctly tallies non-compliant and compliant terms."""
    f1 = evaluate_contract_vs_statute_slots("SECURITY_DEPOSIT", date(2024, 8, 1), {"deposit_cap_months": 2.0})
    f2 = evaluate_contract_vs_statute_slots("ENTRY_NOTICE", date(2024, 8, 1), {"entry_notice_hours": 48.0})
    resp = synthesize_portfolio_response([f1, f2], "2024-08-01", "CA:Oakland", "Highland LLC")
    assert resp.verdict == "NON_COMPLIANT_TERMS_FOUND"
    assert resp.summary["non_compliant"] == 1
    assert resp.summary["compliant"] == 1
    assert resp.summary["total_evaluated"] == 2
