"""
src/backend/main.py
===================
FastAPI REST API Server for KruschBizLaw.
Default loopback binding: 127.0.0.1:8087.
Sovereign Cross-Domain Statutory Compliance Platform ("The Join").
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware

from ..engine.join import evaluate_contract_vs_statute_slots, synthesize_portfolio_response
from ..engine.mandates import STATUTORY_MANDATES
from ..engine.models import (
    ContractVsStatuteRequest,
    ContractVsStatuteResponse,
    ComplianceFinding,
)
from .clients import KruschBizClient, KruschLawClient
from .config import is_strict_loopback, settings, validate_security_invariants

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("kruschbizlaw.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event enforcing security invariants and loopback residency on startup."""
    logger.info("Initializing KruschBizLaw Sovereign Statutory Compliance Platform...")
    validate_security_invariants(settings)
    loopback_ok = is_strict_loopback(settings.HOST)
    logger.info(
        f"KruschBizLaw listening on {settings.HOST}:{settings.PORT} "
        f"[Strict Loopback: {'YES' if loopback_ok else 'NO'}, Env: {settings.APP_ENV}]"
    )
    yield
    logger.info("KruschBizLaw shutting down cleanly.")


app = FastAPI(
    title="KruschBizLaw API",
    version="0.2.0",
    description="Sovereign Cross-Domain Statutory Compliance Engine & Contract-vs-Statute Join Platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

biz_client = KruschBizClient()
law_client = KruschLawClient()


def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    api_key: Optional[str] = Query(None)
) -> Optional[str]:
    """Verify API key outside development or when REQUIRE_API_KEY is enabled."""
    env = (settings.APP_ENV or settings.ENVIRONMENT or "development").lower()
    if env == "development" and not settings.REQUIRE_API_KEY:
        return x_api_key or api_key or "dev_bypass"

    token = x_api_key or api_key
    if not token or (settings.API_KEY and token != settings.API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key."
        )
    return token


@app.get("/health")
def health_check(request: Request) -> Dict[str, Any]:
    """Health & fleet node connectivity check."""
    client_host = request.client.host if request.client else "unknown"
    return {
        "status": "healthy",
        "service": "krusch-bizlaw",
        "version": "0.2.0",
        "environment": settings.APP_ENV,
        "is_strict_loopback": is_strict_loopback(settings.HOST),
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
def evaluate_compliance(
    req: ContractVsStatuteRequest,
    _auth: Optional[str] = Depends(verify_api_key)
) -> ContractVsStatuteResponse:
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
        as_of = datetime.strptime(req.as_of_date.strip(), "%Y-%m-%d").date()
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
            clause = biz_client.get_controlling_clause(
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
    property_type: str = "residential",
    _auth: Optional[str] = Depends(verify_api_key)
) -> ComplianceFinding:
    """Evaluate an arbitrary clause string directly against statutory mandates."""
    if not as_of_date or not as_of_date.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Non-negotiable Invariant: 'as_of_date' is mandatory. No silent 'today' is permitted."
        )

    try:
        as_of = datetime.strptime(as_of_date.strip(), "%Y-%m-%d").date()
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
