"""
src/backend/main.py
===================
FastAPI REST API Server for KruschBizLaw.
Default loopback binding: 127.0.0.1:8087.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ..engine.join import evaluate_contract_vs_statute_slots, synthesize_portfolio_response
from ..engine.mandates import STATUTORY_MANDATES, resolve_statutory_mandate
from ..engine.models import (
    ContractVsStatuteRequest,
    ContractVsStatuteResponse,
    ComplianceFinding,
)
from .clients import KruschBizClient, KruschLawClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("kruschbizlaw.api")

app = FastAPI(
    title="KruschBizLaw API",
    version="0.1.0-alpha.1",
    description="Sovereign Cross-Domain Statutory Compliance Engine & Contract-vs-Statute Join Platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

biz_client = KruschBizClient()
law_client = KruschLawClient()


@app.get("/health")
def health_check(request: Request) -> Dict[str, Any]:
    """Health & fleet node connectivity check."""
    client_host = request.client.host if request.client else "unknown"
    return {
        "status": "healthy",
        "service": "krusch-bizlaw",
        "version": "0.1.0-alpha.1",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "client_host": client_host,
        "fleet_connectivity": {
            "krusch_biz": biz_client.check_health(),
            "krusch_law": law_client.check_health(),
        }
    }


@app.get("/api/mandates")
def list_statutory_mandates() -> Dict[str, Any]:
    """Enumerate recognized statutory floors, ceilings, and prohibitions."""
    return {
        "total": len(STATUTORY_MANDATES),
        "mandates": STATUTORY_MANDATES
    }


@app.post("/api/conflicts/contract-vs-statute", response_model=ContractVsStatuteResponse)
def evaluate_compliance(req: ContractVsStatuteRequest) -> ContractVsStatuteResponse:
    """
    Primary Join endpoint:
    Compares controlling contract clause slots against statutory floors and ceilings.
    """
    if not req.as_of_date or not req.as_of_date.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Non-negotiable Invariant: 'as_of_date' is mandatory. No silent 'today' is permitted."
        )

    try:
        as_of = datetime.strptime(req.as_of_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: '{req.as_of_date}'. Expected YYYY-MM-DD."
        )

    findings: List[ComplianceFinding] = []

    for topic in req.topics:
        # Check if direct slot override was supplied in request
        contract_slots = req.contract_slots or {}
        clause_info = None

        # If connected to KruschBiz and counterparty specified, consult live DAG
        if req.counterparty and not contract_slots:
            clause = biz_client.consult_controlling_clause(
                counterparty=req.counterparty,
                topic=topic,
                as_of_date=req.as_of_date
            )
            if clause:
                clause_info = {
                    "instrument": clause.get("agreement_title"),
                    "section": clause.get("section"),
                    "span": clause.get("content"),
                    "normalized_slot": clause.get("structured_slots", {}),
                    "authority_class": clause.get("authority_class")
                }
                contract_slots = clause.get("structured_slots", {})

        # If raw text was supplied in request, build clause info
        if req.contract_clause_text and not clause_info:
            clause_info = {
                "instrument": "Uploaded / Injected Provision",
                "section": "Active Section",
                "span": req.contract_clause_text,
                "normalized_slot": contract_slots,
                "authority_class": "candidate_clause"
            }

        finding = evaluate_contract_vs_statute_slots(
            topic=topic,
            as_of=as_of,
            contract_slots=contract_slots,
            contract_clause_info=clause_info,
            property_type=req.property_type or "residential"
        )
        findings.append(finding)

    return synthesize_portfolio_response(
        findings=findings,
        as_of_date=req.as_of_date,
        jurisdiction=req.jurisdiction,
        counterparty=req.counterparty
    )


@app.post("/api/evaluate/clause")
def evaluate_single_clause(
    topic: str,
    as_of_date: str,
    clause_text: str,
    property_type: str = "residential"
) -> ComplianceFinding:
    """Evaluate an arbitrary clause string directly against statutory mandates."""
    try:
        as_of = datetime.strptime(as_of_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: '{as_of_date}'. Expected YYYY-MM-DD."
        )

    clause_info = {
        "instrument": "User Submission",
        "section": "1.0",
        "span": clause_text,
        "normalized_slot": {}
    }

    return evaluate_contract_vs_statute_slots(
        topic=topic,
        as_of=as_of,
        contract_clause_info=clause_info,
        property_type=property_type
    )
