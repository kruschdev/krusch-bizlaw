"""
src/engine/join.py
==================
Core Deterministic Join Evaluation Engine for KruschBizLaw.
Evaluates normalized contract slots against statutory floors, ceilings,
and non-waivable public policy prohibitions.
"""

from __future__ import annotations

import re
import uuid
from datetime import date
from typing import Any, Dict, List, Optional

from .mandates import normalize_topic, resolve_statutory_mandate
from .models import (
    AlignmentVerdict,
    ComplianceFinding,
    ContractVsStatuteResponse,
    EnforceabilityVerdict,
)


def evaluate_contract_vs_statute_slots(
    topic: str,
    as_of: date,
    contract_slots: Optional[Dict[str, Any]] = None,
    contract_clause_info: Optional[Dict[str, Any]] = None,
    property_type: str = "residential",
    statute_override: Optional[Dict[str, Any]] = None,
) -> ComplianceFinding:
    """
    Deterministically evaluate a single contract clause's slots against
    the governing statutory mandate for a topic as of a specific date.
    """
    topic_norm = normalize_topic(topic)
    trace_id = f"trace_bizlaw_{uuid.uuid4().hex[:12]}"

    # Resolve governing statute
    statute_info = statute_override or resolve_statutory_mandate(
        topic=topic_norm,
        as_of=as_of,
        property_type=property_type
    )

    contract_slots = contract_slots or (contract_clause_info.get("normalized_slot") if contract_clause_info else {}) or {}

    # Case A: Both absent
    if not contract_clause_info and not contract_slots and not statute_info:
        return ComplianceFinding(
            topic=topic_norm,
            alignment=AlignmentVerdict.COVERAGE_GAP.value,
            enforceability=EnforceabilityVerdict.UNSPECIFIED.value,
            coverage="partial",
            contract_clause=None,
            controlling_statute=None,
            explanation=f"Topic '{topic_norm}' not found in contract portfolio nor recognized statutory registry.",
            trace_id=trace_id
        )

    # Case B: Contract absent, Statute exists
    if not contract_clause_info and not contract_slots:
        return ComplianceFinding(
            topic=topic_norm,
            alignment=AlignmentVerdict.COVERAGE_GAP.value,
            enforceability=EnforceabilityVerdict.UNSPECIFIED.value,
            coverage="partial",
            contract_clause=None,
            controlling_statute=statute_info,
            explanation=f"Mandatory statute '{statute_info.get('citation')}' exists, but no operative contract clause was provided.",
            trace_id=trace_id
        )

    # Case C: Statute absent, Contract exists
    if not statute_info:
        return ComplianceFinding(
            topic=topic_norm,
            alignment=AlignmentVerdict.ALIGNED.value,
            enforceability=EnforceabilityVerdict.ENFORCEABLE.value,
            coverage="partial",
            contract_clause=contract_clause_info,
            controlling_statute=None,
            explanation=f"Contract terms govern; no preemptive statutory mandate found for '{topic_norm}'.",
            trace_id=trace_id
        )

    # Extract raw content for regex fallback if needed
    raw_content = contract_clause_info.get("span", "") if contract_clause_info else ""

    alignment = AlignmentVerdict.ALIGNED.value
    enforceability = EnforceabilityVerdict.ENFORCEABLE.value
    explanation = f"Contract terms comply with statutory requirements under {statute_info['citation']}."

    # 1. SECURITY DEPOSIT / COMMERCIAL SECURITY DEPOSIT
    if topic_norm in ("SECURITY_DEPOSIT", "COMMERCIAL_SECURITY_DEPOSIT"):
        is_comm = (
            property_type == "commercial"
            or topic_norm == "COMMERCIAL_SECURITY_DEPOSIT"
            or (contract_clause_info and "commercial" in (contract_clause_info.get("instrument") or "").lower())
        )

        if is_comm and topic_norm != "SECURITY_DEPOSIT":
            statute_info["citation"] = "Cal. Civ. Code § 1950.7(f)"
            statute_info["mandate_type"] = "STATUTORY_PERMISSIVE_WAIVER"
            alignment = AlignmentVerdict.ALIGNED.value
            enforceability = EnforceabilityVerdict.ENFORCEABLE.value
            explanation = (
                "Commercial tenancy deposit governed by Cal. Civ. Code § 1950.7; freedom of contract applies "
                "and statutory 1-month residential cap under AB 12 is inapplicable."
            )
        elif is_comm and property_type == "commercial":
            statute_info["citation"] = "Cal. Civ. Code § 1950.7"
            statute_info["mandate_type"] = "STATUTORY_PERMISSIVE_WAIVER"
            alignment = AlignmentVerdict.ALIGNED.value
            enforceability = EnforceabilityVerdict.ENFORCEABLE.value
            explanation = (
                "Commercial tenancy security deposit governed by Cal. Civ. Code § 1950.7; "
                "AB 12 1-month ceiling does not apply to commercial real property leases."
            )
        else:
            stat_cap = statute_info["normalized_slot"].get("deposit_cap_months", 1.0)
            contract_val = (
                contract_slots.get("deposit_cap_months")
                or contract_slots.get("deposit_months")
                or contract_slots.get("max_months")
                or contract_slots.get("security_deposit_months")
            )
            if contract_val is None and raw_content:
                m = re.search(r"(\d+(?:\.\d+)?)\s*(?:months?'?\s*(?:rent|deposit))", raw_content, re.IGNORECASE)
                if m:
                    contract_val = float(m.group(1))

            if contract_val is not None:
                contract_val = float(contract_val)
                if contract_val > stat_cap:
                    alignment = AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
                    enforceability = EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value
                    explanation = (
                        f"Contract demands {contract_val} months rent security deposit, violating non-waivable statutory ceiling of "
                        f"{stat_cap} month(s) under {statute_info['citation']} as of {as_of}."
                    )
                else:
                    alignment = AlignmentVerdict.ALIGNED.value
                    enforceability = EnforceabilityVerdict.ENFORCEABLE.value
                    explanation = f"Contract deposit of {contract_val} months conforms to statutory ceiling ({stat_cap} months)."

    # 2. ENTRY NOTICE
    elif topic_norm == "ENTRY_NOTICE":
        stat_min = statute_info["normalized_slot"].get("entry_notice_hours", 24.0)
        contract_val = (
            contract_slots.get("entry_notice_hours")
            or contract_slots.get("notice_hours")
            or contract_slots.get("min_hours")
        )
        if contract_val is None and raw_content:
            m = re.search(r"(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)(?:\s+\w+){0,3}\s+notice", raw_content, re.IGNORECASE)
            if not m:
                m = re.search(r"(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)", raw_content, re.IGNORECASE)
            if m:
                contract_val = float(m.group(1))

        if contract_val is not None:
            contract_val = float(contract_val)
            if contract_val < stat_min:
                alignment = AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
                enforceability = EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value
                explanation = (
                    f"Contract provides {contract_val} hours entry notice, violating statutory minimum floor of "
                    f"{stat_min} hours under {statute_info['citation']}."
                )
            elif contract_val > stat_min:
                alignment = AlignmentVerdict.CONTRACT_MORE_GENEROUS.value
                enforceability = EnforceabilityVerdict.ENFORCEABLE.value
                explanation = f"Contract grants {contract_val} hours advance notice, exceeding statutory floor of {stat_min} hours."
            else:
                alignment = AlignmentVerdict.ALIGNED.value
                enforceability = EnforceabilityVerdict.ENFORCEABLE.value
                explanation = f"Contract entry notice ({contract_val} hrs) matches statutory minimum requirement."

    # 3. DEPOSIT RETURN TIMELINE
    elif topic_norm == "DEPOSIT_RETURN":
        stat_max_days = statute_info["normalized_slot"].get("deposit_return_days", 21.0)
        contract_days = (
            contract_slots.get("deposit_return_days")
            or contract_slots.get("return_days")
            or contract_slots.get("accounting_days")
        )
        if contract_days is None and raw_content:
            m = re.search(r"(\d+)\s*(?:calendar\s+|business\s+)?days?", raw_content, re.IGNORECASE)
            if m:
                contract_days = float(m.group(1))

        if contract_days is not None:
            contract_days = float(contract_days)
            if contract_days > stat_max_days:
                alignment = AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
                enforceability = EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value
                explanation = (
                    f"Contract allows {contract_days} days for security deposit return, violating non-waivable statutory ceiling of "
                    f"{stat_max_days} calendar days under {statute_info['citation']}."
                )
            elif contract_days < stat_max_days:
                alignment = AlignmentVerdict.CONTRACT_MORE_GENEROUS.value
                enforceability = EnforceabilityVerdict.ENFORCEABLE.value
                explanation = f"Contract provides expedited deposit return within {contract_days} days (statutory ceiling: {stat_max_days} days)."
            else:
                alignment = AlignmentVerdict.ALIGNED.value
                enforceability = EnforceabilityVerdict.ENFORCEABLE.value
                explanation = f"Contract return timeline ({contract_days} days) conforms to statutory 21-day requirement."

    # 4. HABITABILITY WAIVER & REPAIR-AND-DEDUCT
    elif topic_norm in ("HABITABILITY_WAIVER", "REPAIR_AND_DEDUCT"):
        waives_hab = contract_slots.get("waives_habitability") or contract_slots.get("habitability_waiver")
        waives_repair = contract_slots.get("waives_repair_deduct") or contract_slots.get("repair_deduct_waiver")

        # Fallback text scan
        if waives_hab is None and waives_repair is None and raw_content:
            lower = raw_content.lower()
            if "as-is" in lower or "waives" in lower or "1941" in lower or "1942" in lower:
                waives_hab = True
                waives_repair = True

        if waives_hab or waives_repair:
            alignment = AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
            enforceability = EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value
            explanation = (
                f"Contract purports to waive habitability or repair-and-deduct remedies, which is void as contrary "
                f"to public policy under {statute_info['citation']}."
            )
        else:
            alignment = AlignmentVerdict.ALIGNED.value
            enforceability = EnforceabilityVerdict.ENFORCEABLE.value
            explanation = f"No prohibited habitability waivers detected; compliant with {statute_info['citation']}."

    # 5. RETALIATION WAIVER
    elif topic_norm == "RETALIATION_WAIVER":
        waives_retal = contract_slots.get("waives_retaliation_defense") or contract_slots.get("retaliation_waiver")
        if waives_retal is None and raw_content:
            lower = raw_content.lower()
            if "retaliat" in lower and "waiv" in lower:
                waives_retal = True

        if waives_retal:
            alignment = AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
            enforceability = EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value
            explanation = (
                f"Contract purports to waive statutory retaliation defenses, which is void as contrary to "
                f"public policy under {statute_info['citation']}."
            )
        else:
            alignment = AlignmentVerdict.ALIGNED.value
            enforceability = EnforceabilityVerdict.ENFORCEABLE.value
            explanation = f"No prohibited retaliation waivers detected; compliant with {statute_info['citation']}."

    # 6. LATE FEE LIQUIDATED DAMAGES
    elif topic_norm == "LATE_FEE":
        stat_max_pct = statute_info["normalized_slot"].get("max_pct", 5.0)
        contract_pct = (
            contract_slots.get("late_penalty_pct")
            or contract_slots.get("late_fee_pct")
            or contract_slots.get("penalty_pct")
        )
        if contract_pct is None and raw_content:
            m = re.search(r"(\d+(?:\.\d+)?)\s*%", raw_content)
            if m:
                contract_pct = float(m.group(1))

        if contract_pct is not None:
            contract_pct = float(contract_pct)
            if contract_pct > stat_max_pct:
                alignment = AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
                enforceability = EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value
                explanation = (
                    f"Contract late charge of {contract_pct}% exceeds the customary statutory reasonable liquidated "
                    f"damages ceiling of {stat_max_pct}% under {statute_info['citation']}."
                )
            else:
                alignment = AlignmentVerdict.ALIGNED.value
                enforceability = EnforceabilityVerdict.ENFORCEABLE.value
                explanation = f"Contract late fee ({contract_pct}%) conforms to statutory reasonableness ceiling ({stat_max_pct}%)."

    # 7. USURY / PAYMENT TERMS
    elif topic_norm == "PAYMENT_TERMS":
        stat_max_apr = statute_info["normalized_slot"].get("max_pct", 10.0)
        contract_interest = (
            contract_slots.get("late_interest_pct")
            or contract_slots.get("interest_pct")
            or contract_slots.get("annual_interest_pct")
        )
        if contract_interest is None and raw_content:
            m = re.search(r"(\d+(?:\.\d+)?)\s*%\s*(?:per\s+annum|annual|interest)", raw_content, re.IGNORECASE)
            if m:
                contract_interest = float(m.group(1))

        if contract_interest is not None:
            contract_interest = float(contract_interest)
            if contract_interest > stat_max_apr:
                alignment = AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value
                enforceability = EnforceabilityVerdict.VOID_AS_AGAINST_PUBLIC_POLICY.value
                explanation = (
                    f"Contract interest rate of {contract_interest}% per annum violates the California constitutional "
                    f"usury ceiling of {stat_max_apr}% under {statute_info['citation']}."
                )
            else:
                alignment = AlignmentVerdict.ALIGNED.value
                enforceability = EnforceabilityVerdict.ENFORCEABLE.value
                explanation = f"Contract interest rate ({contract_interest}%) conforms to constitutional usury ceiling ({stat_max_apr}%)."

    return ComplianceFinding(
        topic=topic_norm,
        alignment=alignment,
        enforceability=enforceability,
        coverage="partial",
        contract_clause=contract_clause_info,
        controlling_statute=statute_info,
        explanation=explanation,
        trace_id=trace_id
    )


def synthesize_portfolio_response(
    findings: List[ComplianceFinding],
    as_of_date: str,
    jurisdiction: str,
    counterparty: Optional[str] = None
) -> ContractVsStatuteResponse:
    """Synthesize overall portfolio verdict and metrics summary from findings."""
    compliant_count = 0
    non_compliant_count = 0
    coverage_gap_count = 0

    for f in findings:
        if f.alignment == AlignmentVerdict.CONTRACT_LESS_THAN_MANDATORY.value:
            non_compliant_count += 1
        elif f.alignment == AlignmentVerdict.COVERAGE_GAP.value:
            coverage_gap_count += 1
        else:
            compliant_count += 1

    if non_compliant_count > 0:
        verdict = "NON_COMPLIANT_TERMS_FOUND"
    elif coverage_gap_count > 0:
        verdict = "COVERAGE_GAPS_IDENTIFIED"
    else:
        verdict = "COMPLIANT"

    return ContractVsStatuteResponse(
        verdict=verdict,
        as_of_date=as_of_date,
        jurisdiction=jurisdiction,
        counterparty=counterparty,
        coverage_completeness="partial",
        findings=findings,
        summary={
            "compliant": compliant_count,
            "non_compliant": non_compliant_count,
            "coverage_gaps": coverage_gap_count,
            "total_evaluated": len(findings)
        }
    )
