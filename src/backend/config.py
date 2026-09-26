"""
src/backend/config.py
=====================
Centralized configuration, security invariants, and data residency enforcement
for the KruschBizLaw Cross-Domain Statutory Compliance Platform.
Default residency: Strict loopback (127.0.0.1:8087).
"""

from __future__ import annotations

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized configuration for KruschBizLaw backend."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Service & Networking
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    APP_ENV: str = os.getenv("APP_ENV", os.getenv("ENVIRONMENT", "development"))
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8087"))
    ALLOW_LAN: bool = os.getenv("ALLOW_LAN", "0") in ("1", "true", "True")

    # Security & API Key Invariants
    REQUIRE_API_KEY: bool = os.getenv("REQUIRE_API_KEY", "false").lower() in ("true", "1", "yes")
    API_KEY: Optional[str] = os.getenv("API_KEY", None)

    # Fleet Service Endpoints (Air-Gapped Loopback Mesh)
    BIZ_BASE_URL: str = os.getenv("BIZ_BASE_URL", "http://127.0.0.1:8086")
    LAW_BASE_URL: str = os.getenv("LAW_BASE_URL", "http://127.0.0.1:8085")
    CLIENT_TIMEOUT: float = float(os.getenv("CLIENT_TIMEOUT", "5.0"))

    # CORS
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:8507,http://127.0.0.1:8507,http://localhost:3000,http://127.0.0.1:3000"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


def is_loopback_or_private_host(url_or_host: str) -> bool:
    """Inspect whether a configured host/URL resides strictly on loopback or private networks."""
    import ipaddress
    import urllib.parse

    if not url_or_host:
        return False
    try:
        if "://" in url_or_host:
            hostname = urllib.parse.urlparse(url_or_host).hostname or ""
        else:
            hostname = url_or_host

        hostname = hostname.strip().lower()
        if (
            hostname in ("localhost", "127.0.0.1", "::1", "host.docker.internal", "db", "backend", "frontend")
            or hostname.startswith("mock-")
            or hostname.endswith(".local")
            or hostname.endswith(".internal")
        ):
            return True
        ip = ipaddress.ip_address(hostname)
        return ip.is_loopback or ip.is_private
    except Exception:
        return False


def is_strict_loopback(url_or_host: str) -> bool:
    """Inspect whether a configured host/URL resides strictly on loopback (127.0.0.1, localhost, ::1)."""
    import ipaddress
    import urllib.parse

    if not url_or_host:
        return False
    try:
        if "://" in url_or_host:
            hostname = urllib.parse.urlparse(url_or_host).hostname or ""
        else:
            hostname = url_or_host

        hostname = hostname.strip().lower()
        if hostname in ("localhost", "127.0.0.1", "::1") or hostname.startswith("mock-"):
            return True
        ip = ipaddress.ip_address(hostname)
        return ip.is_loopback
    except Exception:
        return False


def validate_security_invariants(s: Settings) -> None:
    """
    Enforce security invariants:
      1. API key mandatory outside development if REQUIRE_API_KEY or APP_ENV != 'development'.
      2. Non-loopback binding forbidden unless ALLOW_LAN=1 is explicitly set.
      3. In production, host and fleet endpoints must reside strictly on loopback unless ALLOW_LAN=1.
    """
    disallowed_keys = ("", "default", "changeme", "secret", "replace_me")
    env = (s.APP_ENV or s.ENVIRONMENT or "development").lower()

    if env != "development" and (not s.API_KEY or not s.API_KEY.strip() or s.API_KEY.strip().lower() in disallowed_keys):
        raise RuntimeError(
            "Security Violation: A non-default API_KEY is strictly required outside development environment (APP_ENV != 'development')."
        )

    if (s.HOST == "0.0.0.0" or not is_loopback_or_private_host(s.HOST)) and not s.ALLOW_LAN:
        raise RuntimeError(
            f"Security Violation: Refusing to bind to non-loopback host '{s.HOST}' without ALLOW_LAN=1."
        )

    if not is_loopback_or_private_host(s.BIZ_BASE_URL) and not s.ALLOW_LAN:
        raise RuntimeError(
            f"Security Violation: Refusing connection to non-local KruschBiz host '{s.BIZ_BASE_URL}' without ALLOW_LAN=1."
        )

    if not is_loopback_or_private_host(s.LAW_BASE_URL) and not s.ALLOW_LAN:
        raise RuntimeError(
            f"Security Violation: Refusing connection to non-local KruschLaw host '{s.LAW_BASE_URL}' without ALLOW_LAN=1."
        )

    # Invariant: In production without ALLOW_LAN, process never leaves loopback
    if env == "production" and not s.ALLOW_LAN:
        if not is_strict_loopback(s.HOST):
            raise RuntimeError(
                f"Security Violation: Production host must be strictly loopback (127.0.0.1) without ALLOW_LAN=1, got '{s.HOST}'."
            )
        if not is_strict_loopback(s.BIZ_BASE_URL):
            raise RuntimeError(
                f"Security Violation: Production KruschBiz endpoint must reside strictly on loopback without ALLOW_LAN=1, got '{s.BIZ_BASE_URL}'."
            )
        if not is_strict_loopback(s.LAW_BASE_URL):
            raise RuntimeError(
                f"Security Violation: Production KruschLaw endpoint must reside strictly on loopback without ALLOW_LAN=1, got '{s.LAW_BASE_URL}'."
            )


settings = Settings()
