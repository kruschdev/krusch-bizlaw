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
        "PAYMENT_TERMS"
    ]
    for key in expected_keys:
        assert key in STATUTORY_MANDATES


def test_topic_normalization():
    """Verify alias mapping."""
    assert normalize_topic("deposit_return_days") == "DEPOSIT_RETURN"
    assert normalize_topic("repair_deduct") == "REPAIR_AND_DEDUCT"
    assert normalize_topic("usury") == "PAYMENT_TERMS"
    assert normalize_topic("habitability") == "HABITABILITY_WAIVER"


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
