"""
tests/unit/test_join_properties.py
==================================
Property-based mutation test suite for KruschBizLaw.
Verifies that parameter mutations across statutory thresholds, temporal boundaries,
property types, and syntax variants deterministically flip or maintain legal verdicts.
"""

from __future__ import annotations

from datetime import date, timedelta

from src.engine.join import evaluate_contract_vs_statute_slots
from src.engine.models import AlignmentVerdict, EnforceabilityVerdict


class TestJoinPropertyMutations:
    """Property-based invariant and mutation tests."""

    def test_property_deposit_cap_mutation(self):
        """Mutating deposit cap across 1.0 month post-AB 12 threshold."""
        as_of = date(2024, 8, 1)

        # Compliant range: <= 1.0
        for months in [0.5, 0.75, 0.9, 1.0]:
            f = evaluate_contract_vs_statute_slots(
                topic="SECURITY_DEPOSIT",
                as_of=as_of,
                contract_slots={"deposit_cap_months": months},
                property_type="residential"
            )
            assert f.alignment == AlignmentVerdict.ALIGNED.value, f"Failed at {months} months"
            assert f.enforceability == EnforceabilityVerdict.ENFORCEABLE.value

        # Non-compliant range: > 1.0
        for months in [1.01, 1.1, 1.5, 2.0, 3.0]:
            f = evaluate_contract_vs_statute_slots(
                topic="SECURITY_DEPOSIT",
                as_of=as_of,
                contract_slots={"deposit_cap_months": months},
                property_type="residential"
            )
            assert f.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value, f"Failed at {months} months"
            assert f.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value

    def test_property_temporal_boundary_mutation(self):
        """Mutating as_of_date across the AB 12 effective date (2024-07-01) for a 2.0-month lease."""
        deposit_months = 2.0
        boundary = date(2024, 7, 1)

        # Days before July 1, 2024 -> ALIGNED
        for delta in [1, 7, 30, 90, 180]:
            test_date = boundary - timedelta(days=delta)
            f = evaluate_contract_vs_statute_slots(
                topic="SECURITY_DEPOSIT",
                as_of=test_date,
                contract_slots={"deposit_cap_months": deposit_months},
                property_type="residential"
            )
            assert f.alignment == AlignmentVerdict.ALIGNED.value, f"Failed on {test_date}"
            assert f.enforceability == EnforceabilityVerdict.ENFORCEABLE.value

        # Days on or after July 1, 2024 -> VOID
        for delta in [0, 1, 7, 30, 90, 180]:
            test_date = boundary + timedelta(days=delta)
            f = evaluate_contract_vs_statute_slots(
                topic="SECURITY_DEPOSIT",
                as_of=test_date,
                contract_slots={"deposit_cap_months": deposit_months},
                property_type="residential"
            )
            assert f.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value, f"Failed on {test_date}"
            assert f.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value

    def test_property_entry_notice_mutation(self):
        """Mutating entry notice hours across statutory 24.0-hour floor."""
        as_of = date(2024, 8, 1)

        # Sub-statutory: < 24.0
        for hours in [1.0, 6.0, 12.0, 23.5, 23.9]:
            f = evaluate_contract_vs_statute_slots(
                topic="ENTRY_NOTICE",
                as_of=as_of,
                contract_slots={"entry_notice_hours": hours}
            )
            assert f.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value, f"Failed at {hours} hrs"
            assert f.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value

        # Exactly statutory floor: 24.0
        f_exact = evaluate_contract_vs_statute_slots(
            topic="ENTRY_NOTICE",
            as_of=as_of,
            contract_slots={"entry_notice_hours": 24.0}
        )
        assert f_exact.alignment == AlignmentVerdict.ALIGNED.value
        assert f_exact.enforceability == EnforceabilityVerdict.ENFORCEABLE.value

        # More generous: > 24.0
        for hours in [24.1, 36.0, 48.0, 72.0]:
            f = evaluate_contract_vs_statute_slots(
                topic="ENTRY_NOTICE",
                as_of=as_of,
                contract_slots={"entry_notice_hours": hours}
            )
            assert f.alignment == AlignmentVerdict.CONTRACT_MORE_GENEROUS.value, f"Failed at {hours} hrs"
            assert f.enforceability == EnforceabilityVerdict.ENFORCEABLE.value

    def test_property_deposit_return_mutation(self):
        """Mutating deposit return days across statutory 21.0-day ceiling."""
        as_of = date(2024, 8, 1)

        # More generous / expedited: < 21.0
        for days in [1.0, 7.0, 14.0, 20.0]:
            f = evaluate_contract_vs_statute_slots(
                topic="DEPOSIT_RETURN",
                as_of=as_of,
                contract_slots={"deposit_return_days": days}
            )
            assert f.alignment == AlignmentVerdict.CONTRACT_MORE_GENEROUS.value, f"Failed at {days} days"
            assert f.enforceability == EnforceabilityVerdict.ENFORCEABLE.value

        # Exactly statutory ceiling: 21.0
        f_exact = evaluate_contract_vs_statute_slots(
            topic="DEPOSIT_RETURN",
            as_of=as_of,
            contract_slots={"deposit_return_days": 21.0}
        )
        assert f_exact.alignment == AlignmentVerdict.ALIGNED.value
        assert f_exact.enforceability == EnforceabilityVerdict.ENFORCEABLE.value

        # Sub-statutory / delayed: > 21.0
        for days in [21.5, 25.0, 30.0, 45.0, 60.0]:
            f = evaluate_contract_vs_statute_slots(
                topic="DEPOSIT_RETURN",
                as_of=as_of,
                contract_slots={"deposit_return_days": days}
            )
            assert f.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value, f"Failed at {days} days"
            assert f.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value

    def test_property_commercial_lease_mutation(self):
        """Mutating property_type from residential to commercial flips 3.0-month deposit from VOID to ENFORCEABLE."""
        as_of = date(2024, 8, 1)
        slots = {"deposit_cap_months": 3.0}

        # Residential -> VOID under AB 12
        f_res = evaluate_contract_vs_statute_slots(
            topic="SECURITY_DEPOSIT",
            as_of=as_of,
            contract_slots=slots,
            property_type="residential"
        )
        assert f_res.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
        assert f_res.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value

        # Commercial -> ENFORCEABLE under § 1950.7(f)
        f_comm = evaluate_contract_vs_statute_slots(
            topic="SECURITY_DEPOSIT",
            as_of=as_of,
            contract_slots=slots,
            property_type="commercial"
        )
        assert f_comm.alignment == AlignmentVerdict.ALIGNED.value
        assert f_comm.enforceability == EnforceabilityVerdict.ENFORCEABLE.value

    def test_property_late_fee_mutation(self):
        """Mutating late fee percent across 5.0% customary liquidated damages ceiling."""
        as_of = date(2024, 8, 1)

        for pct in [1.0, 3.0, 5.0]:
            f = evaluate_contract_vs_statute_slots(
                topic="LATE_FEE",
                as_of=as_of,
                contract_slots={"late_penalty_pct": pct}
            )
            assert f.alignment == AlignmentVerdict.ALIGNED.value
            assert f.enforceability == EnforceabilityVerdict.ENFORCEABLE.value

        for pct in [5.1, 7.5, 10.0, 15.0]:
            f = evaluate_contract_vs_statute_slots(
                topic="LATE_FEE",
                as_of=as_of,
                contract_slots={"late_penalty_pct": pct}
            )
            assert f.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
            assert f.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value

    def test_property_word_number_normalization(self):
        """Spelled-out words in raw clauses match numeric extraction correctly."""
        as_of = date(2024, 8, 1)

        # "two months rent" vs "2 months rent"
        f_word = evaluate_contract_vs_statute_slots(
            topic="SECURITY_DEPOSIT",
            as_of=as_of,
            contract_clause_info={
                "instrument": "Lease",
                "section": "3.1",
                "span": "Tenant shall provide two months rent deposit.",
                "normalized_slot": {}
            }
        )
        assert f_word.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
        assert f_word.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value

        # "forty-five days" vs "45 days"
        f_days = evaluate_contract_vs_statute_slots(
            topic="DEPOSIT_RETURN",
            as_of=as_of,
            contract_clause_info={
                "instrument": "Lease",
                "section": "4.2",
                "span": "Landlord will return deposit within forty-five days.",
                "normalized_slot": {}
            }
        )
        assert f_days.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
        assert f_days.enforceability == EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value
