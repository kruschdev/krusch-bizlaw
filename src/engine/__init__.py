"""KruschBizLaw Engine package."""
from .models import (
    ContractVsStatuteRequest,
    ContractVsStatuteResponse,
    ComplianceFinding,
    MandateType,
    EnforceabilityVerdict,
    AlignmentVerdict,
)
from .mandates import STATUTORY_MANDATES, TOPIC_ALIASES, resolve_statutory_mandate
from .join import evaluate_contract_vs_statute_slots

__all__ = [
    "ContractVsStatuteRequest",
    "ContractVsStatuteResponse",
    "ComplianceFinding",
    "MandateType",
    "EnforceabilityVerdict",
    "AlignmentVerdict",
    "STATUTORY_MANDATES",
    "TOPIC_ALIASES",
    "resolve_statutory_mandate",
    "evaluate_contract_vs_statute_slots",
]
