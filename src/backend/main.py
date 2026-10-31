"""
src/backend/main.py
===================
FastAPI REST API Server for KruschBizLaw.
Default loopback binding: 127.0.0.1:8087.
Sovereign Cross-Domain Statutory Compliance Platform ("The Join").
"""

from __future__ import annotations

import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, status

from ..engine.join import evaluate_contract_vs_statute_slots, synthesize_portfolio_response
from ..engine.mandates import STATUTORY_MANDATES
from ..engine.models import (
    ComplianceFinding,
    ContractVsStatuteRequest,
    ContractVsStatuteResponse,
)
from .clients import KruschBizClient, KruschLawClient
from .config import is_strict_loopback, settings, validate_security_invariants

_MONOREPO_LIB_PY = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "lib-py")
)
if os.path.isdir(_MONOREPO_LIB_PY) and _MONOREPO_LIB_PY not in sys.path:
    sys.path.insert(0, _MONOREPO_LIB_PY)

try:
    from krusch_toolkit.fastapi_app import (  # noqa: E402
        create_fastapi_app,
        error_envelope,
        ok_envelope,
    )
except ImportError:  # pragma: no cover - standalone CI clone fallback without monorepo lib-py
    _FALLBACK_HTTP_STATUS_CODES: Dict[int, str] = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        408: "REQUEST_TIMEOUT",
        409: "CONFLICT",
        413: "PAYLOAD_TOO_LARGE",
        422: "VALIDATION_ERROR",
        423: "LOCKED",
        424: "FAILED_DEPENDENCY",
        429: "RATE_LIMITED",
        500: "INTERNAL_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
        504: "GATEWAY_TIMEOUT",
    }

    def ok_envelope(
        tool: str, summary: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return {
            "ok": True,
            "tool": str(tool or "fastapi"),
            "summary": str(summary or "OK"),
            "data": {} if data is None else data,
        }

    def error_envelope(
        code: str,
        message: str,
        details: Any = None,
        tool: str = "fastapi",
    ) -> Dict[str, Any]:
        resolved_code = str(code or "INTERNAL_ERROR")
        resolved_message = str(message or "Request failed")
        return {
            "ok": False,
            "tool": str(tool or "fastapi"),
            "summary": str(message or code or "Request failed"),
            "error": {
                "code": resolved_code,
                "message": resolved_message,
                **({"details": details} if details is not None else {}),
            },
        }

    def create_fastapi_app(
        title: str = "Krusch Service",
        version: str = "1.0.0",
        *,
        description: str = "",
        docs_url: Optional[str] = "/docs",
        redoc_url: Optional[str] = "/redoc",
        service_name: Optional[str] = None,
        cors_origins: Optional[List[str]] = None,
        allow_credentials: Optional[bool] = None,
        lifespan: Any = None,
        health_check: Any = None,
        flatten_health_payload: bool = False,
        legacy_error_detail: bool = False,
        startup_hooks: Optional[List[Any]] = None,
        shutdown_hooks: Optional[List[Any]] = None,
        logger: Any = None,
    ) -> FastAPI:
        import inspect
        import re
        import time
        import uuid
        from fastapi.encoders import jsonable_encoder
        from fastapi.exceptions import RequestValidationError
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.responses import JSONResponse
        from starlette.exceptions import HTTPException as StarletteHTTPException

        resolved_name = (
            service_name.strip()
            if service_name and service_name.strip()
            else (
                re.sub(r"[^a-z0-9]+", "-", (title or "krusch-service").lower()).strip("-")
                or "krusch-service"
            )
        )
        active_logger = logger or logging.getLogger(resolved_name)
        start_list = list(startup_hooks or [])
        stop_list = list(shutdown_hooks or [])
        custom_lifespan = lifespan

        def _sanitize_token(raw: Optional[str]) -> str:
            return raw.replace("\r", "").replace("\n", "").strip() if raw else ""

        def _normalize_origins(origins: Optional[List[str]]) -> List[str]:
            if origins is None:
                return ["*"]
            cleaned: List[str] = []
            for raw in origins:
                if not isinstance(raw, str) or "\r" in raw or "\n" in raw:
                    continue
                token = raw.strip()
                if token and token.lower() not in ("null", "false"):
                    cleaned.append(token)
            return cleaned

        def _accepts_pos_arg(fn: Any) -> bool:
            try:
                sig = inspect.signature(fn)
            except (TypeError, ValueError):
                return False
            return any(
                p.kind
                in (
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    inspect.Parameter.VAR_POSITIONAL,
                )
                for p in sig.parameters.values()
            )

        @asynccontextmanager
        async def _composed_lifespan(app_instance: FastAPI):
            primary_exc: Optional[BaseException] = None
            try:
                for hook in start_list:
                    res = hook()
                    if inspect.isawaitable(res):
                        await res
                if custom_lifespan is not None:
                    async with custom_lifespan(app_instance):
                        yield
                else:
                    yield
            except BaseException as exc:
                primary_exc = exc
                raise
            finally:
                first_err: Optional[Exception] = None
                for hook in stop_list:
                    try:
                        res = hook()
                        if inspect.isawaitable(res):
                            await res
                    except Exception as exc:
                        active_logger.exception("Shutdown hook failed in %s", resolved_name)
                        if first_err is None:
                            first_err = exc
                if first_err is not None and primary_exc is None:
                    raise first_err

        app_inst = FastAPI(
            title=title,
            description=description,
            version=version,
            docs_url=docs_url,
            redoc_url=redoc_url,
            lifespan=_composed_lifespan,
        )

        resolved_origins = _normalize_origins(cors_origins)
        safe_creds = len(resolved_origins) > 0 and "*" not in resolved_origins
        resolved_allow_creds = (
            safe_creds
            if allow_credentials is None
            else (bool(allow_credentials) and safe_creds)
        )
        app_inst.add_middleware(
            CORSMiddleware,
            allow_origins=resolved_origins,
            allow_credentials=resolved_allow_creds,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        def _attach_headers(request: Request, response: Any) -> None:
            state = getattr(request, "state", None)
            req_id = getattr(state, "request_id", None)
            if not req_id:
                req_id = _sanitize_token(request.headers.get("x-request-id")) or str(uuid.uuid4())
                if state is not None:
                    state.request_id = req_id
            start_t = getattr(state, "request_start_time", None)
            elapsed_ms = (
                max(0.0, (time.perf_counter() - start_t) * 1000.0)
                if start_t is not None
                else 0.0
            )
            response.headers["X-Request-ID"] = str(req_id)
            response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.2f}"
            response.headers["X-Content-Type-Options"] = "nosniff"

        def _attach_cors_fallback(request: Request, response: Any) -> None:
            if not resolved_origins or "access-control-allow-origin" in response.headers:
                return
            if "*" in resolved_origins:
                response.headers["Access-Control-Allow-Origin"] = "*"
                return
            existing_vary = response.headers.get("vary", "")
            vary_tokens = [v.strip().lower() for v in existing_vary.split(",") if v.strip()]
            if "origin" not in vary_tokens:
                response.headers["Vary"] = f"{existing_vary}, Origin" if existing_vary else "Origin"
            raw_origin = request.headers.get("origin")
            if not isinstance(raw_origin, str) or "\r" in raw_origin or "\n" in raw_origin:
                return
            clean_origin = raw_origin.strip()
            if (
                clean_origin
                and clean_origin.lower() not in ("null", "false")
                and clean_origin in resolved_origins
            ):
                response.headers["Access-Control-Allow-Origin"] = clean_origin
                if resolved_allow_creds:
                    response.headers["Access-Control-Allow-Credentials"] = "true"

        @app_inst.middleware("http")
        async def _request_context_middleware(request: Request, call_next: Any) -> Any:
            request.state.request_id = (
                _sanitize_token(request.headers.get("x-request-id")) or str(uuid.uuid4())
            )
            request.state.request_start_time = time.perf_counter()
            response = await call_next(request)
            _attach_headers(request, response)
            return response

        @app_inst.exception_handler(StarletteHTTPException)
        async def _http_exception_handler(
            request: Request, exc: StarletteHTTPException
        ) -> JSONResponse:
            status_code = int(getattr(exc, "status_code", 500) or 500)
            code = _FALLBACK_HTTP_STATUS_CODES.get(status_code, f"HTTP_{status_code}")
            raw_detail = getattr(exc, "detail", None)
            details: Any = None
            if isinstance(raw_detail, str):
                message = raw_detail
            elif isinstance(raw_detail, dict):
                code = str(raw_detail.get("code") or code)
                message = str(
                    raw_detail.get("message") or raw_detail.get("detail") or f"HTTP {status_code}"
                )
                details = raw_detail.get("details", raw_detail)
            elif raw_detail is not None:
                message = f"HTTP {status_code}"
                details = jsonable_encoder(raw_detail)
            else:
                message = f"HTTP {status_code}"
            err_content = error_envelope(code, message, details=details, tool=resolved_name)
            if legacy_error_detail:
                err_content["detail"] = (
                    jsonable_encoder(raw_detail) if raw_detail is not None else message
                )
            response = JSONResponse(
                status_code=status_code,
                content=err_content,
                headers=dict(getattr(exc, "headers", None) or {}),
            )
            _attach_headers(request, response)
            _attach_cors_fallback(request, response)
            return response

        @app_inst.exception_handler(RequestValidationError)
        async def _validation_exception_handler(
            request: Request, exc: RequestValidationError
        ) -> JSONResponse:
            encoded = jsonable_encoder(exc.errors())
            err_content = error_envelope(
                "VALIDATION_ERROR",
                "Request validation failed",
                details=encoded,
                tool=resolved_name,
            )
            if legacy_error_detail:
                err_content["detail"] = encoded
            response = JSONResponse(status_code=422, content=err_content)
            _attach_headers(request, response)
            _attach_cors_fallback(request, response)
            return response

        @app_inst.exception_handler(Exception)
        async def _unhandled_exception_handler(request: Request, _exc: Exception) -> JSONResponse:
            active_logger.exception(
                "Unhandled exception in %s on %s %s",
                resolved_name,
                getattr(request, "method", "UNKNOWN"),
                getattr(getattr(request, "url", None), "path", "/"),
            )
            response = JSONResponse(
                status_code=500,
                content=error_envelope(
                    "INTERNAL_ERROR", "Internal server error", tool=resolved_name
                ),
            )
            _attach_headers(request, response)
            _attach_cors_fallback(request, response)
            return response

        accepts_req = _accepts_pos_arg(health_check) if health_check is not None else False

        async def _evaluate_health(request: Request, *, flatten: bool) -> JSONResponse:
            extra: Any = None
            if health_check is not None:
                try:
                    extra = health_check(request) if accepts_req else health_check()
                    if inspect.isawaitable(extra):
                        extra = await extra
                except Exception as exc:
                    active_logger.warning("Health check failed in %s: %s", resolved_name, exc)
                    msg = str(exc) or "Service unhealthy"
                    err_body = error_envelope("UNHEALTHY", msg, tool=resolved_name)
                    if legacy_error_detail:
                        err_body["detail"] = msg
                    return JSONResponse(status_code=503, content=err_body)

                if extra is False or (isinstance(extra, dict) and extra.get("ok") is False):
                    msg = (
                        str(extra.get("summary") or extra.get("message") or "Service unhealthy")
                        if isinstance(extra, dict)
                        else "Service unhealthy"
                    )
                    err_body = error_envelope(
                        "UNHEALTHY",
                        msg,
                        details=extra if isinstance(extra, dict) else None,
                        tool=resolved_name,
                    )
                    if legacy_error_detail:
                        err_body["detail"] = msg
                    return JSONResponse(status_code=503, content=err_body)

            payload = {
                "service": resolved_name,
                "version": version,
                **(extra if isinstance(extra, dict) else {}),
            }
            env = ok_envelope(resolved_name, "Service healthy", payload)
            body = {**payload, **env} if flatten else env
            return JSONResponse(status_code=200, content=body)

        async def _probe_health(request: Any) -> Any:
            return await _evaluate_health(request, flatten=bool(flatten_health_payload))

        async def _probe_doctor(request: Any) -> Any:
            return await _evaluate_health(request, flatten=False)

        _probe_health.__annotations__ = {"request": Request, "return": Any}
        _probe_doctor.__annotations__ = {"request": Request, "return": Any}

        app_inst.add_api_route("/health", _probe_health, methods=["GET"], tags=["ops"])
        app_inst.add_api_route("/doctor", _probe_doctor, methods=["GET"], tags=["ops"])
        return app_inst

__all__ = [
    "app",
    "create_fastapi_app",
    "error_envelope",
    "health_check",
    "lifespan",
    "ok_envelope",
]

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("kruschbizlaw.api")


def _init_service_clients(app_instance: FastAPI) -> None:
    """Safely initialize downstream KruschBiz and KruschLaw clients onto app.state (ARCH-01, BUG-01)."""
    try:
        app_instance.state.biz_client = KruschBizClient()
    except (ValueError, httpx.HTTPError, RuntimeError, OSError) as exc:
        logger.error("Failed to create biz client: %s", exc, exc_info=True)
        app_instance.state.biz_client = None

    try:
        app_instance.state.law_client = KruschLawClient()
    except (ValueError, httpx.HTTPError, RuntimeError, OSError) as exc:
        logger.error("Failed to create law client: %s", exc, exc_info=True)
        app_instance.state.law_client = None


def _get_biz_client(request: Request) -> Optional[KruschBizClient]:
    if request is None or not hasattr(request.app.state, "biz_client"):
        raise RuntimeError("biz_client is not initialized on request.app.state")
    return request.app.state.biz_client


def _get_law_client(request: Request) -> Optional[KruschLawClient]:
    if request is None or not hasattr(request.app.state, "law_client"):
        raise RuntimeError("law_client is not initialized on request.app.state")
    return request.app.state.law_client


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """Lifecycle event enforcing security invariants, client initialization, and loopback residency on startup."""
    logger.info("Initializing KruschBizLaw Sovereign Statutory Compliance Platform...")
    validate_security_invariants(settings)
    _init_service_clients(app_instance)
    loopback_ok = is_strict_loopback(settings.HOST)
    logger.info(
        f"KruschBizLaw listening on {settings.HOST}:{settings.PORT} "
        f"[Strict Loopback: {'YES' if loopback_ok else 'NO'}, Env: {settings.APP_ENV}]"
    )
    yield
    logger.info("KruschBizLaw shutting down cleanly.")


def _safe_check_health(client: Any, name: str) -> Any:
    if client is None:
        return "unreachable"
    try:
        return client.check_health()
    except (httpx.HTTPError, RuntimeError, ValueError, OSError):
        logger.error("%s health check failed", name, exc_info=True)
        return "unreachable"


def health_check(request: Request) -> Dict[str, Any]:
    """Health & fleet node connectivity check."""
    client_host = request.client.host if request.client else "unknown"
    active_biz = _get_biz_client(request)
    active_law = _get_law_client(request)
    return {
        "status": "healthy",
        "service": "krusch-bizlaw",
        "version": "0.2.0",
        "environment": settings.APP_ENV,
        "is_strict_loopback": is_strict_loopback(settings.HOST),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "client_host": client_host,
        "fleet_connectivity": {
            "krusch_biz": _safe_check_health(active_biz, "biz_client"),
            "krusch_law": _safe_check_health(active_law, "law_client"),
        },
    }


app = create_fastapi_app(
    title="KruschBizLaw API",
    version="0.2.0",
    description="Sovereign Cross-Domain Statutory Compliance Engine & Contract-vs-Statute Join Platform",
    service_name="krusch-bizlaw",
    cors_origins=settings.cors_origins_list,
    allow_credentials=True,
    lifespan=lifespan,
    health_check=health_check,
    flatten_health_payload=True,
    legacy_error_detail=True,
    logger=logger,
)
_init_service_clients(app)


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
    request: Request,
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
    active_biz = _get_biz_client(request)

    for topic in req.topics:
        # Check if direct slot override was supplied in request
        contract_slots = req.contract_slots or {}
        clause_info = None

        # If connected to KruschBiz and counterparty specified, consult live DAG
        if req.counterparty and not contract_slots and active_biz is not None:
            clause = active_biz.get_controlling_clause(
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
            property_type=req.property_type or "residential",
            include_precedents=bool(getattr(req, "include_precedents", False))
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
    include_precedents: bool = False,
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
        property_type=property_type,
        include_precedents=include_precedents
    )
