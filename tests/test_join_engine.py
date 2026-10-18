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


def test_controlling_precedents_retrieval():
    """Verify that include_precedents=True populates controlling_precedents list."""
    finding = evaluate_contract_vs_statute_slots(
        topic="SECURITY_DEPOSIT",
        as_of=date(2024, 8, 1),
        contract_slots={"deposit_cap_months": 2.0},
        property_type="residential",
        include_precedents=True
    )
    assert finding.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
    assert isinstance(finding.controlling_precedents, list)
    if finding.controlling_precedents:
        p = finding.controlling_precedents[0]
        assert "citation" in p
        assert "score" in p


def test_non_compete_clause_void():
    """Non-compete covenant is void as against public policy under BPC § 16600."""
    finding = evaluate_contract_vs_statute_slots(
        topic="NON_COMPETE",
        as_of=date(2024, 8, 1),
        contract_slots={"restrains_trade": True},
        raw_content="Employee agrees not to engage in competing business for 2 years after separation."
    )
    assert finding.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
    assert finding.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value
    assert "16600" in finding.controlling_statute["citation"]


def test_non_compete_compliant():
    """Contract without non-compete restraints conforms to BPC § 16600."""
    finding = evaluate_contract_vs_statute_slots(
        topic="NON_COMPETE",
        as_of=date(2024, 8, 1),
        contract_slots={"restrains_trade": False},
        raw_content="Employee agrees to protect confidential trade secrets during employment."
    )
    assert finding.alignment == AlignmentVerdict.ALIGNED.value
    assert finding.enforceability == EnforceabilityVerdict.ENFORCEABLE.value


def test_exculpatory_clause_void():
    """Clause exempting gross negligence or willful injury is void under CC § 1668."""
    finding = evaluate_contract_vs_statute_slots(
        topic="EXCULPATORY_CLAUSE",
        as_of=date(2024, 8, 1),
        contract_slots={"waives_gross_negligence": True},
        raw_content="Vendor shall have no liability for any gross negligence or willful misconduct."
    )
    assert finding.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
    assert finding.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value
    assert "1668" in finding.controlling_statute["citation"]


def test_exculpatory_clause_compliant():
    """Standard commercial liability cap excluding willful harm is enforceable."""
    finding = evaluate_contract_vs_statute_slots(
        topic="EXCULPATORY_CLAUSE",
        as_of=date(2024, 8, 1),
        contract_slots={"waives_gross_negligence": False},
        raw_content="In no event shall liability exceed total fees paid under this agreement."
    )
    assert finding.alignment == AlignmentVerdict.ALIGNED.value
    assert finding.enforceability == EnforceabilityVerdict.ENFORCEABLE.value


def test_unilateral_attorney_fee_preempted():
    """Unilateral fee clause is preempted and rendered reciprocal under CC § 1717."""
    finding = evaluate_contract_vs_statute_slots(
        topic="ATTORNEY_FEE_RECIPROCITY",
        as_of=date(2024, 8, 1),
        contract_slots={"unilateral_fee_shifting": True},
        raw_content="Borrower shall pay all attorney's fees incurred by Lender in enforcement."
    )
    assert finding.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
    assert finding.enforceability == EnforceabilityVerdict.PREEMPTED.value
    assert "1717" in finding.controlling_statute["citation"]


def test_bilateral_attorney_fee_enforceable():
    """Mutual prevailing party fee clause is enforceable under CC § 1717."""
    finding = evaluate_contract_vs_statute_slots(
        topic="ATTORNEY_FEE_RECIPROCITY",
        as_of=date(2024, 8, 1),
        contract_slots={"unilateral_fee_shifting": False},
        raw_content="The prevailing party in any action shall be entitled to recover reasonable attorney fees."
    )
    assert finding.alignment == AlignmentVerdict.ALIGNED.value
    assert finding.enforceability == EnforceabilityVerdict.ENFORCEABLE.value


def test_employee_expense_waiver_void():
    """Employee bearing business expenses is void under LC § 2802 and § 2804."""
    finding = evaluate_contract_vs_statute_slots(
        topic="EXPENSE_REIMBURSEMENT",
        as_of=date(2024, 8, 1),
        contract_slots={"waives_reimbursement": True},
        raw_content="Remote employee shall provide cellular phone and high-speed internet at employee's own expense with no reimbursement."
    )
    assert finding.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
    assert finding.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value
    assert "2802" in finding.controlling_statute["citation"]


def test_employee_expense_reimbursement_compliant():
    """Contract reimbursing employee expenditures conforms to LC § 2802."""
    finding = evaluate_contract_vs_statute_slots(
        topic="EXPENSE_REIMBURSEMENT",
        as_of=date(2024, 8, 1),
        contract_slots={"waives_reimbursement": False},
        raw_content="Employer shall indemnify employee for all reasonable and necessary business expenses."
    )
    assert finding.alignment == AlignmentVerdict.ALIGNED.value
    assert finding.enforceability == EnforceabilityVerdict.ENFORCEABLE.value


def test_invention_assignment_broad_void():
    """Demanding all inventions developed on employee's own time is void under LC § 2870."""
    finding = evaluate_contract_vs_statute_slots(
        topic="INVENTION_ASSIGNMENT",
        as_of=date(2024, 8, 1),
        contract_slots={"assigns_all_inventions": True},
        raw_content="Employee assigns all inventions whether or not conceived on employee's own time or outside working hours."
    )
    assert finding.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
    assert finding.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value
    assert "2870" in finding.controlling_statute["citation"]


def test_invention_assignment_with_carveout_compliant():
    """Invention assignment with express § 2870 statutory notice is enforceable."""
    finding = evaluate_contract_vs_statute_slots(
        topic="INVENTION_ASSIGNMENT",
        as_of=date(2024, 8, 1),
        contract_slots={"assigns_all_inventions": False},
        raw_content="Inventions are assigned subject to the statutory exclusions of California Labor Code Section 2870."
    )
    assert finding.alignment == AlignmentVerdict.ALIGNED.value
    assert finding.enforceability == EnforceabilityVerdict.ENFORCEABLE.value


def test_consumer_privacy_waiver_void():
    """Waiver of CCPA/CPRA consumer deletion rights is void under CC § 1798.192."""
    finding = evaluate_contract_vs_statute_slots(
        topic="CONSUMER_PRIVACY_WAIVER",
        as_of=date(2024, 8, 1),
        contract_slots={"waives_privacy_rights": True},
        raw_content="Consumer agrees to waive all statutory privacy rights and has no right to delete personal information."
    )
    assert finding.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
    assert finding.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value
    assert "1798.192" in finding.controlling_statute["citation"]


def test_automatic_renewal_call_to_cancel_void():
    """Requiring phone call or certified mail to cancel is void under ARL (BPC § 17602)."""
    finding = evaluate_contract_vs_statute_slots(
        topic="AUTOMATIC_RENEWAL",
        as_of=date(2024, 8, 1),
        contract_slots={"no_online_cancellation": True},
        raw_content="Subscription auto-renews monthly; subscriber must call to cancel during business hours with no online cancellation."
    )
    assert finding.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
    assert finding.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value
    assert "17602" in finding.controlling_statute["citation"]


def test_automatic_renewal_online_cancel_compliant():
    """Subscription with affirmative consent and exclusive online cancellation is compliant."""
    finding = evaluate_contract_vs_statute_slots(
        topic="AUTOMATIC_RENEWAL",
        as_of=date(2024, 8, 1),
        contract_slots={"no_online_cancellation": False},
        raw_content="Subscriber may cancel the monthly continuous service subscription online at any time via account settings."
    )
    assert finding.alignment == AlignmentVerdict.ALIGNED.value
    assert finding.enforceability == EnforceabilityVerdict.ENFORCEABLE.value



