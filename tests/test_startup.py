"""
tests/test_startup.py
=====================
Unit tests verifying resilient FastAPI lifespan client construction and health reporting
when KruschBizClient or KruschLawClient construction fails (ARCH-01, BUG-01, BUG-02, TEST-01).
"""

from fastapi.testclient import TestClient
import src.backend.main as main_mod
from src.backend.clients import KruschBizClient, KruschLawClient


def test_startup_survives_client_construction_failure(monkeypatch):
    def _failing_init(self, *args, **kwargs):
        raise RuntimeError("client construction failed")

    monkeypatch.setattr(KruschBizClient, "__init__", _failing_init)
    monkeypatch.setattr(KruschLawClient, "__init__", _failing_init)

    with TestClient(main_mod.app) as client:
        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["fleet_connectivity"]["krusch_biz"] == "unreachable"
        assert data["fleet_connectivity"]["krusch_law"] == "unreachable"


def test_startup_fails_on_invalid_security_configuration(monkeypatch):
    # BUG-02: Lifespan startup invokes validate_security_invariants and aborts on invalid settings
    import pytest
    monkeypatch.setattr(main_mod.settings, "HOST", "0.0.0.0")
    monkeypatch.setattr(main_mod.settings, "ALLOW_LAN", False)

    with pytest.raises(RuntimeError, match="Refusing to bind to non-loopback host"):
        with TestClient(main_mod.app):
            pass


def test_service_clients_stored_solely_on_app_state():
    # ARCH-01: No module-level biz_client or law_client globals; missing state raises RuntimeError
    import pytest
    from types import SimpleNamespace

    assert not hasattr(main_mod, "biz_client")
    assert not hasattr(main_mod, "law_client")

    fake_req = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace()))
    with pytest.raises(RuntimeError, match="biz_client is not initialized"):
        main_mod._get_biz_client(fake_req)
    with pytest.raises(RuntimeError, match="law_client is not initialized"):
        main_mod._get_law_client(fake_req)

