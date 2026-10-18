"""
src/engine/mandates.py
======================
Statutory Mandates Registry for KruschBizLaw.
Defines non-waivable statutory floors, ceilings, and prohibitions under California
and municipal legal authorities, with first-class temporal awareness.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Optional


STATUTORY_MANDATES: dict[str, dict[str, Any]] = {
    "SECURITY_DEPOSIT": {
        "citation": "Cal. Civ. Code § 1950.5(c)(1)",
        "mandate_type": "STATUTORY_CEILING",
        "pre_ab12_ceiling": 2.0,      # Prior to July 1, 2024: 2 months unfurnished rent
        "post_ab12_ceiling": 1.0,     # On or after July 1, 2024 (AB 12): 1 month rent
        "ab12_effective_date": date(2024, 7, 1),
        "slot_key": "deposit_cap_months",
        "unit": "months_rent",
        "statutory_text": "A landlord may not demand or receive security in an amount exceeding one month's rent (AB 12, effective July 1, 2024).",
        "non_waivable": True,
    },
    "ENTRY_NOTICE": {
        "citation": "Cal. Civ. Code § 1954(d)(1)",
        "mandate_type": "STATUTORY_FLOOR",
        "minimum_hours": 24.0,        # 24 hours written notice minimum
        "slot_key": "entry_notice_hours",
        "unit": "hours",
        "statutory_text": "The landlord shall give the tenant reasonable written notice of the landlord's intent to enter, with 24 hours presumed reasonable.",
        "non_waivable": True,
    },
    "DEPOSIT_RETURN": {
        "citation": "Cal. Civ. Code § 1950.5(g)(1)",
        "mandate_type": "STATUTORY_CEILING",
        "max_return_days": 21.0,      # 21 calendar days ceiling
        "slot_key": "deposit_return_days",
        "unit": "calendar_days",
        "statutory_text": "No later than 21 calendar days after the tenant has vacated the premises, the landlord shall furnish a copy of an itemized statement along with the remaining portion of the security deposit.",
        "non_waivable": True,
    },
    "HABITABILITY_WAIVER": {
        "citation": "Cal. Civ. Code § 1942.1",
        "mandate_type": "STATUTORY_PROHIBITION",
        "slot_key": "waives_habitability",
        "unit": "prohibited_waiver",
        "statutory_text": "Any agreement by a tenant by which he waives or modifies his rights under Section 1941 or 1942 shall be void as contrary to public policy.",
        "non_waivable": True,
    },
    "REPAIR_AND_DEDUCT": {
        "citation": "Cal. Civ. Code § 1942.1",
        "mandate_type": "STATUTORY_PROHIBITION",
        "slot_key": "waives_repair_deduct",
        "unit": "prohibited_waiver",
        "statutory_text": "Any agreement by a tenant waiving repair-and-deduct remedies under Section 1942 shall be void as contrary to public policy.",
        "non_waivable": True,
    },
    "COMMERCIAL_SECURITY_DEPOSIT": {
        "citation": "Cal. Civ. Code § 1950.7(f)",
        "mandate_type": "STATUTORY_PERMISSIVE_WAIVER",
        "slot_key": "commercial_deposit_waiver",
        "unit": "permissive_waiver",
        "statutory_text": "In commercial leases, parties may contractually agree to terms different from Section 1950.7 or waive statutory deposit return provisions (Civ. Code § 1950.7(f)).",
        "non_waivable": False,
    },
    "RETALIATION_WAIVER": {
        "citation": "Cal. Civ. Code § 1942.5(h)",
        "mandate_type": "STATUTORY_PROHIBITION",
        "slot_key": "waives_retaliation_defense",
        "unit": "prohibited_waiver",
        "statutory_text": "Any waiver by a tenant of rights under Section 1942.5 shall be void as contrary to public policy.",
        "non_waivable": True,
    },
    "LATE_FEE": {
        "citation": "Cal. Civ. Code § 1671(d)",
        "mandate_type": "STATUTORY_CEILING",
        "max_penalty_pct": 5.0,       # Customary 5% liquidated damages ceiling
        "slot_key": "late_penalty_pct",
        "unit": "percent",
        "statutory_text": "Late fees must represent a reasonable endeavor to estimate fair average compensation for the loss sustained by late payment.",
        "non_waivable": True,
    },
    "PAYMENT_TERMS": {
        "citation": "Cal. Const. Art. XV § 1",
        "mandate_type": "STATUTORY_CEILING",
        "max_annual_interest_pct": 10.0,
        "slot_key": "late_interest_pct",
        "unit": "percent_per_annum",
        "statutory_text": "The maximum legal rate of interest for non-exempt commercial obligations is 10 percent per annum.",
        "non_waivable": True,
    },
    "NON_COMPETE": {
        "citation": "Cal. Bus. & Prof. Code § 16600",
        "mandate_type": "STATUTORY_PROHIBITION",
        "slot_key": "restraint_of_trade",
        "unit": "prohibited_covenant",
        "statutory_text": "Every contract by which anyone is restrained from engaging in a lawful profession, trade, or business of any kind is to that extent void (AB 1076 & SB 699).",
        "non_waivable": True,
    },
    "EXCULPATORY_CLAUSE": {
        "citation": "Cal. Civ. Code § 1668",
        "mandate_type": "STATUTORY_PROHIBITION",
        "slot_key": "exemption_from_liability",
        "unit": "prohibited_waiver",
        "statutory_text": "All contracts which have for their object to exempt anyone from responsibility for his own fraud, willful injury, or violation of law are void as contrary to public policy.",
        "non_waivable": True,
    },
    "ATTORNEY_FEE_RECIPROCITY": {
        "citation": "Cal. Civ. Code § 1717",
        "mandate_type": "STATUTORY_FLOOR",
        "slot_key": "reciprocal_attorney_fees",
        "unit": "statutory_mutuality",
        "statutory_text": "Where a contract provides for attorney's fees incurred by one party, the party determined to be the prevailing party shall be entitled to reasonable attorney's fees as a non-waivable reciprocal right.",
        "non_waivable": True,
    },
    "EXPENSE_REIMBURSEMENT": {
        "citation": "Cal. Lab. Code § 2802",
        "mandate_type": "STATUTORY_FLOOR",
        "slot_key": "employee_reimbursement",
        "unit": "mandatory_indemnification",
        "statutory_text": "An employer shall indemnify an employee for all necessary expenditures or losses incurred in direct consequence of discharge of duties. Any waiver is null and void under § 2804.",
        "non_waivable": True,
    },
    "INVENTION_ASSIGNMENT": {
        "citation": "Cal. Lab. Code § 2870",
        "mandate_type": "STATUTORY_PROHIBITION",
        "slot_key": "broad_invention_assignment",
        "unit": "prohibited_assignment",
        "statutory_text": "Employment provisions requiring assignment of inventions developed on employee's own time without employer equipment or trade secrets are void as contrary to public policy (§ 2870/§ 2872).",
        "non_waivable": True,
    },
    "CONSUMER_PRIVACY_WAIVER": {
        "citation": "Cal. Civ. Code § 1798.192 & § 1751",
        "mandate_type": "STATUTORY_PROHIBITION",
        "slot_key": "consumer_statutory_waiver",
        "unit": "prohibited_waiver",
        "statutory_text": "Any contractual waiver or limitation of consumer rights, remedies, or public injunctive relief under CCPA/CPRA or CLRA is strictly void as against public policy.",
        "non_waivable": True,
    },
    "AUTOMATIC_RENEWAL": {
        "citation": "Cal. Bus. & Prof. Code § 17602",
        "mandate_type": "STATUTORY_MANDATE",
        "slot_key": "automatic_renewal_terms",
        "unit": "mandatory_cancellation_mechanism",
        "statutory_text": "Automatic renewal terms must be presented in a clear and conspicuous manner, with affirmative consent and exclusive online cancellation required.",
        "non_waivable": True,
    }
}

TOPIC_ALIASES: dict[str, str] = {
    "DEPOSIT_RETURN_DAYS": "DEPOSIT_RETURN",
    "DEPOSIT_TIMELINE": "DEPOSIT_RETURN",
    "REPAIR_DEDUCT": "REPAIR_AND_DEDUCT",
    "HABITABILITY": "HABITABILITY_WAIVER",
    "USURY": "PAYMENT_TERMS",
    "INTEREST_RATE": "PAYMENT_TERMS",
    "COMMERCIAL_DEPOSIT": "COMMERCIAL_SECURITY_DEPOSIT",
    "NON_COMPETE_CLAUSE": "NON_COMPETE",
    "COVENANT_NOT_TO_COMPETE": "NON_COMPETE",
    "LIABILITY_WAIVER": "EXCULPATORY_CLAUSE",
    "EXCULPATION": "EXCULPATORY_CLAUSE",
    "ATTORNEY_FEES": "ATTORNEY_FEE_RECIPROCITY",
    "FEE_SHIFTING": "ATTORNEY_FEE_RECIPROCITY",
    "EXPENSES": "EXPENSE_REIMBURSEMENT",
    "REMOTE_WORK_EXPENSES": "EXPENSE_REIMBURSEMENT",
    "EMPLOYEE_INVENTIONS": "INVENTION_ASSIGNMENT",
    "INVENTIONS": "INVENTION_ASSIGNMENT",
    "PATENT_ASSIGNMENT": "INVENTION_ASSIGNMENT",
    "CCPA_WAIVER": "CONSUMER_PRIVACY_WAIVER",
    "PRIVACY_WAIVER": "CONSUMER_PRIVACY_WAIVER",
    "CLRA_WAIVER": "CONSUMER_PRIVACY_WAIVER",
    "SUBSCRIPTION_RENEWAL": "AUTOMATIC_RENEWAL",
    "AUTO_RENEW": "AUTOMATIC_RENEWAL",
}


def normalize_topic(topic: str) -> str:
    """Normalize a topic name through canonical aliases."""
    t = topic.strip().upper().replace(" ", "_")
    return TOPIC_ALIASES.get(t, t)


def resolve_statutory_mandate(
    topic: str,
    as_of: date,
    property_type: str = "residential"
) -> Optional[dict[str, Any]]:
    """
    Resolve controlling statutory mandate metadata and normalized slots
    for a given topic and temporal as-of date.
    """
    topic_norm = normalize_topic(topic)
    mandate = STATUTORY_MANDATES.get(topic_norm)
    if not mandate:
        return None

    result = {
        "topic": topic_norm,
        "citation": mandate["citation"],
        "mandate_type": mandate["mandate_type"],
        "span": mandate["statutory_text"],
        "non_waivable": mandate.get("non_waivable", True),
        "normalized_slot": {}
    }

    if topic_norm == "SECURITY_DEPOSIT":
        if property_type == "commercial":
            result["citation"] = "Cal. Civ. Code § 1950.7"
            result["mandate_type"] = "STATUTORY_PERMISSIVE_WAIVER"
            result["non_waivable"] = False
            result["normalized_slot"] = {"commercial_waiver_permitted": True, "freedom_of_contract": True}
        else:
            eff = mandate["ab12_effective_date"]
            cap = mandate["post_ab12_ceiling"] if as_of >= eff else mandate["pre_ab12_ceiling"]
            citation = mandate["citation"] if as_of >= eff else "Cal. Civ. Code § 1950.5(c) (Prior to AB 12)"
            result["citation"] = citation
            result["effective_date"] = "2024-07-01" if as_of >= eff else "2020-01-01"
            result["normalized_slot"] = {"deposit_cap_months": cap, "max_months": cap}

    elif topic_norm == "ENTRY_NOTICE":
        result["normalized_slot"] = {
            "entry_notice_hours": mandate["minimum_hours"],
            "min_hours": mandate["minimum_hours"]
        }

    elif topic_norm == "DEPOSIT_RETURN":
        result["normalized_slot"] = {
            "deposit_return_days": mandate["max_return_days"],
            "max_days": mandate["max_return_days"]
        }

    elif topic_norm in ("HABITABILITY_WAIVER", "REPAIR_AND_DEDUCT"):
        result["normalized_slot"] = {
            "waiver_prohibited": True,
            "statute_voids_waiver": True
        }

    elif topic_norm == "COMMERCIAL_SECURITY_DEPOSIT":
        result["normalized_slot"] = {
            "waiver_permitted": True,
            "freedom_of_contract": True
        }

    elif topic_norm == "RETALIATION_WAIVER":
        result["normalized_slot"] = {
            "waiver_prohibited": True,
            "statute_voids_waiver": True
        }

    elif topic_norm in ("LATE_FEE", "PAYMENT_TERMS"):
        pct = mandate.get("max_penalty_pct") or mandate.get("max_annual_interest_pct", 10.0)
        result["normalized_slot"] = {"max_pct": pct}

    elif topic_norm in ("NON_COMPETE", "EXCULPATORY_CLAUSE"):
        result["normalized_slot"] = {
            "waiver_prohibited": True,
            "statute_voids_covenant": True
        }

    elif topic_norm == "ATTORNEY_FEE_RECIPROCITY":
        result["normalized_slot"] = {
            "unilateral_clause_void": True,
            "statutory_bilateral_mutuality": True
        }

    elif topic_norm == "EXPENSE_REIMBURSEMENT":
        result["normalized_slot"] = {
            "indemnification_mandatory": True,
            "waiver_void_under_2804": True
        }

    elif topic_norm == "INVENTION_ASSIGNMENT":
        result["normalized_slot"] = {
            "own_time_inventions_exempt": True,
            "statute_voids_broad_assignment": True
        }

    elif topic_norm == "CONSUMER_PRIVACY_WAIVER":
        result["normalized_slot"] = {
            "statutory_waiver_prohibited": True,
            "remedies_non_waivable": True
        }

    elif topic_norm == "AUTOMATIC_RENEWAL":
        result["normalized_slot"] = {
            "clear_conspicuous_mandatory": True,
            "exclusive_online_cancellation_required": True
        }

    return result
