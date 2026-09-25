"""
src/engine/models.py
====================
Pydantic schemas and domain models for KruschBizLaw ("The Join").
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MandateType(str, Enum):
    STATUTORY_CEILING = "STATUTORY_CEILING"
    STATUTORY_FLOOR = "STATUTORY_FLOOR"
    STATUTORY_PROHIBITION = "STATUTORY_PROHIBITION"
    STATUTORY_PERMISSIVE_WAIVER = "STATUTORY_PERMISSIVE_WAIVER"


class AlignmentVerdict(str, Enum):
    ALIGNED = "aligned"
    CONTRACT_MORE_GENEROUS = "contract_more_generous"
    CONTRACT_LESS_THAN_MANDATORY = "contract_less_than_mandatory"
    COVERAGE_GAP = "coverage_gap"
    JURISDICTION_MISMATCH = "jurisdiction_mismatch"


class EnforceabilityVerdict(str, Enum):
    ENFORCEABLE = "ENFORCEABLE"
    VOID_AS_AGAINST_PUBLIC_POLICY = "VOID_AS_AGAINST_PUBLIC_POLICY"
    PREEMPTED = "PREEMPTED"
    UNSPECIFIED = "UNSPECIFIED"


class ContractVsStatuteRequest(BaseModel):
    deal_id: Optional[int] = Field(None, description="Optional KruschBiz deal matter ID")
    matter_id: Optional[int] = Field(None, description="Optional KruschLaw legal matter ID")
    counterparty: Optional[str] = Field(None, description="Counterparty or tenant entity name")
    jurisdiction: str = Field("CA:Oakland", description="Jurisdiction code, e.g. 'CA:Oakland', 'California'")
    as_of_date: str = Field(..., description="Mandatory historical or evaluation date (YYYY-MM-DD). No silent 'today'.")
    topics: List[str] = Field(
        default_factory=lambda: ["SECURITY_DEPOSIT", "ENTRY_NOTICE", "LATE_FEE"],
        description="Topics to evaluate against statutory baselines"
    )
    property_type: Optional[str] = Field("residential", description="Property category: 'residential' or 'commercial'")
    contract_slots: Optional[Dict[str, Any]] = Field(None, description="Optional direct slot dictionary for standalone evaluation")
    contract_clause_text: Optional[str] = Field(None, description="Optional raw contract clause text for standalone analysis")


class ComplianceFinding(BaseModel):
    topic: str
    alignment: str                    # aligned, contract_more_generous, contract_less_than_mandatory, coverage_gap, jurisdiction_mismatch
    enforceability: str               # ENFORCEABLE, VOID_AS_AGAINST_PUBLIC_POLICY, PREEMPTED, UNSPECIFIED
    coverage: str = "partial"         # Invariant: Mark every finding coverage: partial unless verified complete
    contract_clause: Optional[Dict[str, Any]] = None
    controlling_statute: Optional[Dict[str, Any]] = None
    explanation: str
    trace_id: str


class ContractVsStatuteResponse(BaseModel):
    verdict: str                      # COMPLIANT, NON_COMPLIANT_TERMS_FOUND, COVERAGE_GAPS_IDENTIFIED
    as_of_date: str
    jurisdiction: str
    counterparty: Optional[str] = None
    coverage_completeness: str = "partial"
    findings: List[ComplianceFinding]
    summary: Optional[Dict[str, int]] = Field(
        default_factory=lambda: {
            "compliant": 0,
            "non_compliant": 0,
            "coverage_gaps": 0,
            "total_evaluated": 0,
        }
    )
