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

    return result
