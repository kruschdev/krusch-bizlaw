"""
tests/test_mandates.py
======================
Unit tests for KruschBizLaw statutory mandates registry.
"""

from datetime import date
from src.engine.mandates import STATUTORY_MANDATES, normalize_topic, resolve_statutory_mandate


def test_mandates_presence():
    """Verify core California statutory doctrines are registered."""
    expected_keys = [
        "SECURITY_DEPOSIT",
        "ENTRY_NOTICE",
        "DEPOSIT_RETURN",
        "HABITABILITY_WAIVER",
        "REPAIR_AND_DEDUCT",
        "COMMERCIAL_SECURITY_DEPOSIT",
        "RETALIATION_WAIVER",
        "LATE_FEE",
        "PAYMENT_TERMS",
        "NON_COMPETE",
        "EXCULPATORY_CLAUSE",
        "ATTORNEY_FEE_RECIPROCITY",
        "EXPENSE_REIMBURSEMENT",
    ]
    for key in expected_keys:
        assert key in STATUTORY_MANDATES


def test_topic_normalization():
    """Verify alias mapping."""
    assert normalize_topic("deposit_return_days") == "DEPOSIT_RETURN"
    assert normalize_topic("repair_deduct") == "REPAIR_AND_DEDUCT"
    assert normalize_topic("usury") == "PAYMENT_TERMS"
    assert normalize_topic("habitability") == "HABITABILITY_WAIVER"
    assert normalize_topic("non_compete_clause") == "NON_COMPETE"
    assert normalize_topic("liability_waiver") == "EXCULPATORY_CLAUSE"
    assert normalize_topic("attorney_fees") == "ATTORNEY_FEE_RECIPROCITY"
    assert normalize_topic("expenses") == "EXPENSE_REIMBURSEMENT"


def test_ab12_temporal_split():
    """Verify AB 12 1-month ceiling on/after 2024-07-01 vs 2-month prior."""
    pre = resolve_statutory_mandate("SECURITY_DEPOSIT", date(2024, 6, 30))
    post = resolve_statutory_mandate("SECURITY_DEPOSIT", date(2024, 7, 1))

    assert pre["normalized_slot"]["deposit_cap_months"] == 2.0
    assert post["normalized_slot"]["deposit_cap_months"] == 1.0


def test_commercial_lease_override():
    """Verify commercial property type overrides residential deposit ceiling."""
    comm = resolve_statutory_mandate("SECURITY_DEPOSIT", date(2024, 8, 1), property_type="commercial")
    assert comm["citation"] == "Cal. Civ. Code § 1950.7"
    assert comm["non_waivable"] is False


def test_new_mandates_resolution():
    """Verify resolution of commercial and labor mandates."""
    nc = resolve_statutory_mandate("NON_COMPETE", date(2024, 8, 1))
    assert nc["citation"] == "Cal. Bus. & Prof. Code § 16600"
    assert nc["non_waivable"] is True
    assert nc["normalized_slot"]["waiver_prohibited"] is True

    ex = resolve_statutory_mandate("EXCULPATORY_CLAUSE", date(2024, 8, 1))
    assert ex["citation"] == "Cal. Civ. Code § 1668"
    assert ex["non_waivable"] is True

    af = resolve_statutory_mandate("ATTORNEY_FEE_RECIPROCITY", date(2024, 8, 1))
    assert af["citation"] == "Cal. Civ. Code § 1717"
    assert af["normalized_slot"]["statutory_bilateral_mutuality"] is True

    er = resolve_statutory_mandate("EXPENSE_REIMBURSEMENT", date(2024, 8, 1))
    assert er["citation"] == "Cal. Lab. Code § 2802"
    assert er["normalized_slot"]["indemnification_mandatory"] is True

