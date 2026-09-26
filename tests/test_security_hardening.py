"""
tests/test_security_hardening.py
================================
Unit tests verifying strict loopback data residency, API key requirements,
and security invariant enforcement for KruschBizLaw.
"""

from __future__ import annotations

import pytest
from src.backend.config import (
    Settings,
    is_loopback_or_private_host,
    is_strict_loopback,
    validate_security_invariants,
)


class TestSecurityHardening:
    """Security invariants and data residency verification."""

    def test_strict_loopback_detection(self):
        """Strict loopback must only accept 127.0.0.1, localhost, and ::1."""
        assert is_strict_loopback("127.0.0.1") is True
        assert is_strict_loopback("localhost") is True
        assert is_strict_loopback("::1") is True
        assert is_strict_loopback("http://127.0.0.1:8087") is True
        assert is_strict_loopback("http://localhost:8087") is True

        # External or LAN interfaces rejected
        assert is_strict_loopback("0.0.0.0") is False
        assert is_strict_loopback("10.0.0.44") is False
        assert is_strict_loopback("192.168.1.50") is False
        assert is_strict_loopback("https://api.external.com") is False

    def test_loopback_or_private_detection(self):
        """Private IP detection accepts RFC 1918 and loopback addresses."""
        assert is_loopback_or_private_host("127.0.0.1") is True
        assert is_loopback_or_private_host("10.0.0.85") is True
        assert is_loopback_or_private_host("192.168.1.1") is True
        assert is_loopback_or_private_host("172.16.0.5") is True

        # Public internet IPs rejected
        assert is_loopback_or_private_host("8.8.8.8") is False
        assert is_loopback_or_private_host("1.1.1.1") is False

    def test_production_requires_non_default_api_key(self):
        """Outside development, a non-empty, non-default API_KEY is strictly required."""
        # Development allows default/empty
        s_dev = Settings(APP_ENV="development", API_KEY=None, HOST="127.0.0.1")
        validate_security_invariants(s_dev)

        # Staging without key raises
        s_stage = Settings(APP_ENV="staging", API_KEY="", HOST="127.0.0.1")
        with pytest.raises(RuntimeError, match="A non-default API_KEY is strictly required"):
            validate_security_invariants(s_stage)

        # Production with placeholder key raises
        s_prod_bad = Settings(APP_ENV="production", API_KEY="changeme", HOST="127.0.0.1")
        with pytest.raises(RuntimeError, match="A non-default API_KEY is strictly required"):
            validate_security_invariants(s_prod_bad)

        # Production with valid key and loopback succeeds
        s_prod_good = Settings(
            APP_ENV="production",
            API_KEY="sovereign-production-key-9988",
            HOST="127.0.0.1",
            BIZ_BASE_URL="http://127.0.0.1:8086",
            LAW_BASE_URL="http://127.0.0.1:8085"
        )
        validate_security_invariants(s_prod_good)

    def test_refuse_binding_to_wildcard_without_allow_lan(self):
        """Binding to 0.0.0.0 without ALLOW_LAN=1 is forbidden."""
        s = Settings(HOST="0.0.0.0", ALLOW_LAN=False)
        with pytest.raises(RuntimeError, match="Refusing to bind to non-loopback host"):
            validate_security_invariants(s)

        # With ALLOW_LAN=True it succeeds
        s_allowed = Settings(HOST="0.0.0.0", ALLOW_LAN=True, API_KEY="dev_key")
        validate_security_invariants(s_allowed)

    def test_production_strict_loopback_enforcement(self):
        """In production without ALLOW_LAN, endpoints must strictly be loopback."""
        s_prod = Settings(
            APP_ENV="production",
            API_KEY="valid-key-xyz",
            HOST="127.0.0.1",
            BIZ_BASE_URL="http://10.0.0.44:8086",  # LAN IP, not strict loopback
            ALLOW_LAN=False
        )
        with pytest.raises(RuntimeError, match="Production KruschBiz endpoint must reside strictly on loopback"):
            validate_security_invariants(s_prod)
