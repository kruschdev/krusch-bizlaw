"""
tests/test_fastapi_lego_shell.py
================================
Unit tests verifying INV-LEGO-25 migration of KruschBizLaw to
`krusch_toolkit.fastapi_app.create_fastapi_app`, including dual `/health`
compatibility, strict `/doctor` envelopes, tracing/security headers,
dual error envelopes (`error` + `detail`), and standalone CI fallback.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from starlette.middleware.cors import CORSMiddleware

import src.backend.main as main_mod


def test_health_dual_envelope_and_top_level_keys():
    client = TestClient(main_mod.app)
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()

    # INV-LEGO-01 envelope keys
    assert body["ok"] is True
    assert body["tool"] == "krusch-bizlaw"
    assert body["summary"] == "Service healthy"
    assert isinstance(body["data"], dict)
    assert "fleet_connectivity" in body["data"]
    assert set(body["data"]["fleet_connectivity"].keys()) == {"krusch_biz", "krusch_law"}

    # Flattened brownfield top-level keys
    assert body["status"] == "healthy"
    assert body["service"] == "krusch-bizlaw"
    assert body["version"] == "0.2.0"
    assert "fleet_connectivity" in body
    assert body["fleet_connectivity"] == body["data"]["fleet_connectivity"]


def test_doctor_strict_inv_lego_01_envelope():
    client = TestClient(main_mod.app)
    res = client.get("/doctor")
    assert res.status_code == 200
    body = res.json()

    assert set(body.keys()) == {"ok", "tool", "summary", "data"}
    assert body["ok"] is True
    assert body["tool"] == "krusch-bizlaw"
    assert body["summary"] == "Service healthy"
    assert body["data"]["service"] == "krusch-bizlaw"
    assert body["data"]["status"] == "healthy"
    assert "fleet_connectivity" in body["data"]


def test_standard_tracing_and_security_headers():
    client = TestClient(main_mod.app)

    res_auto = client.get("/health")
    assert res_auto.status_code == 200
    assert res_auto.headers.get("X-Request-ID")
    assert float(res_auto.headers["X-Response-Time-Ms"]) >= 0.0
    assert res_auto.headers.get("X-Content-Type-Options") == "nosniff"

    custom_id = "req-bizlaw-lego-trace-42"
    res_echo = client.get("/doctor", headers={"X-Request-ID": custom_id})
    assert res_echo.status_code == 200
    assert res_echo.headers.get("X-Request-ID") == custom_id
    assert float(res_echo.headers["X-Response-Time-Ms"]) >= 0.0
    assert res_echo.headers.get("X-Content-Type-Options") == "nosniff"


def test_http_exception_400_and_401_emit_dual_error_envelope(monkeypatch):
    client = TestClient(main_mod.app)

    # 400 Bad Request: missing/blank as_of_date
    res_400 = client.post(
        "/api/conflicts/contract-vs-statute",
        json={"as_of_date": "", "jurisdiction": "CA:Oakland", "topics": ["SECURITY_DEPOSIT"]},
    )
    assert res_400.status_code == 400
    body_400 = res_400.json()
    assert body_400["ok"] is False
    assert body_400["tool"] == "krusch-bizlaw"
    assert body_400["error"]["code"] == "BAD_REQUEST"
    assert "as_of_date" in body_400["error"]["message"]
    assert "as_of_date" in body_400["detail"]
    assert res_400.headers.get("X-Content-Type-Options") == "nosniff"
    assert res_400.headers.get("X-Request-ID")

    # 401 Unauthorized: invalid API key when REQUIRE_API_KEY is active
    monkeypatch.setattr(main_mod.settings, "REQUIRE_API_KEY", True)
    monkeypatch.setattr(main_mod.settings, "API_KEY", "sovereign-test-key-99")

    res_401 = client.post(
        "/api/conflicts/contract-vs-statute",
        headers={"X-API-Key": "invalid-key"},
        json={"as_of_date": "2024-08-01", "jurisdiction": "CA:Oakland", "topics": ["SECURITY_DEPOSIT"]},
    )
    assert res_401.status_code == 401
    body_401 = res_401.json()
    assert body_401["ok"] is False
    assert body_401["tool"] == "krusch-bizlaw"
    assert body_401["error"]["code"] == "UNAUTHORIZED"
    assert "Invalid or missing API key" in body_401["error"]["message"]
    assert body_401["detail"] == "Invalid or missing API key."
    assert res_401.headers.get("X-Content-Type-Options") == "nosniff"


def test_validation_error_422_emits_dual_error_envelope():
    client = TestClient(main_mod.app)
    res_422 = client.post("/api/conflicts/contract-vs-statute", json={})
    assert res_422.status_code == 422
    body_422 = res_422.json()

    assert body_422["ok"] is False
    assert body_422["tool"] == "krusch-bizlaw"
    assert body_422["error"]["code"] == "VALIDATION_ERROR"
    assert body_422["error"]["message"] == "Request validation failed"
    assert isinstance(body_422["error"]["details"], list)
    assert len(body_422["error"]["details"]) > 0
    assert body_422["detail"] == body_422["error"]["details"]
    assert res_422.headers.get("X-Content-Type-Options") == "nosniff"
    assert res_422.headers.get("X-Request-ID")


def test_standalone_ci_fallback_without_krusch_toolkit(monkeypatch):
    orig_isdir = os.path.isdir
    cleaned_path = [p for p in sys.path if not str(p).endswith("lib-py")]
    monkeypatch.setattr(sys, "path", cleaned_path)
    monkeypatch.setattr(
        os.path,
        "isdir",
        lambda p: False if str(p).endswith("lib-py") else orig_isdir(p),
    )
    monkeypatch.setitem(sys.modules, "krusch_toolkit", None)
    monkeypatch.setitem(sys.modules, "krusch_toolkit.fastapi_app", None)

    main_path = Path(main_mod.__file__).resolve()
    spec = importlib.util.spec_from_file_location("src.backend._standalone_ci_main", main_path)
    assert spec is not None and spec.loader is not None
    standalone_mod = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "src.backend._standalone_ci_main", standalone_mod)
    spec.loader.exec_module(standalone_mod)

    # ARCH-01 preserved in standalone fallback
    assert not hasattr(standalone_mod, "biz_client")
    assert not hasattr(standalone_mod, "law_client")

    with TestClient(standalone_mod.app) as client:
        res_health = client.get("/health", headers={"X-Request-ID": "standalone-ci-01"})
        assert res_health.status_code == 200
        assert res_health.headers.get("X-Request-ID") == "standalone-ci-01"
        assert res_health.headers.get("X-Content-Type-Options") == "nosniff"
        assert float(res_health.headers["X-Response-Time-Ms"]) >= 0.0
        h_body = res_health.json()
        assert h_body["ok"] is True
        assert h_body["tool"] == "krusch-bizlaw"
        assert h_body["status"] == "healthy"
        assert "fleet_connectivity" in h_body
        assert "fleet_connectivity" in h_body["data"]

        res_doc = client.get("/doctor")
        assert res_doc.status_code == 200
        d_body = res_doc.json()
        assert set(d_body.keys()) == {"ok", "tool", "summary", "data"}

        res_400 = client.post(
            "/api/conflicts/contract-vs-statute",
            json={"as_of_date": "   ", "jurisdiction": "CA:Oakland", "topics": ["SECURITY_DEPOSIT"]},
        )
        assert res_400.status_code == 400
        b_400 = res_400.json()
        assert b_400["ok"] is False
        assert b_400["error"]["code"] == "BAD_REQUEST"
        assert "as_of_date" in b_400["detail"]

        res_422 = client.post("/api/conflicts/contract-vs-statute", json={})
        assert res_422.status_code == 422
        b_422 = res_422.json()
        assert b_422["ok"] is False
        assert b_422["error"]["code"] == "VALIDATION_ERROR"
        assert isinstance(b_422["detail"], list)

    # Verify wildcard CORS clamps allow_credentials=False in standalone fallback
    wildcard_app = standalone_mod.create_fastapi_app(
        title="Wildcard Check",
        cors_origins=["*"],
        allow_credentials=True,
    )
    cors_mw = next(m for m in wildcard_app.user_middleware if m.cls is CORSMiddleware)
    assert cors_mw.kwargs["allow_credentials"] is False

    # Verify BUG-02 lifespan security invariant propagation in standalone fallback
    monkeypatch.setattr(standalone_mod.settings, "HOST", "0.0.0.0")
    monkeypatch.setattr(standalone_mod.settings, "ALLOW_LAN", False)
    with pytest.raises(RuntimeError, match="Refusing to bind to non-loopback host"):
        with TestClient(standalone_mod.app):
            pass


def test_portable_paths_contain_no_workstation_home_prefix():
    forbidden_prefix = os.sep + "home" + os.sep + "krusch"
    repo_root = Path(main_mod.__file__).resolve().parents[2]
    for folder in ("src", "tests"):
        for py_file in (repo_root / folder).rglob("*.py"):
            source = py_file.read_text(encoding="utf-8")
            assert forbidden_prefix not in source, f"Found non-portable path in {py_file.name}"
