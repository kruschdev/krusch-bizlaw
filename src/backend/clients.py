"""
src/backend/clients.py
======================
Service Client Adapters for KruschBiz and KruschLaw.
Enables KruschBizLaw to communicate with running fleet nodes:
  - KruschBiz (127.0.0.1:8086): Commercial contract precedence & clause extraction
  - KruschLaw (127.0.0.1:8085): Statutory authority graph & legal RAG
Includes graceful fallbacks for local standalone operation and air-gapped testing.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
import httpx

from .config import settings

logger = logging.getLogger("kruschbizlaw.clients")


class KruschBizClient:
    """Client for querying KruschBiz commercial contract engine."""

    def __init__(self, base_url: Optional[str] = None, timeout: Optional[float] = None):
        self.base_url = (base_url or settings.BIZ_BASE_URL).rstrip("/")
        self.timeout = timeout if timeout is not None else settings.CLIENT_TIMEOUT

    def check_health(self) -> bool:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(f"{self.base_url}/health")
                return res.status_code == 200
        except Exception:
            return False

    def get_controlling_clause(
        self,
        counterparty: str,
        topic: str,
        as_of_date: str,
        tenant_id: str = "org_default"
    ) -> Optional[Dict[str, Any]]:
        """Query KruschBiz GET /api/resolver/controlling-clause to resolve the governing clause."""
        url = f"{self.base_url}/api/resolver/controlling-clause"
        params = {
            "counterparty": counterparty,
            "topic": topic,
            "as_of_date": as_of_date
        }
        headers = {"X-Tenant-ID": tenant_id}
        if settings.API_KEY:
            headers["X-API-Key"] = settings.API_KEY

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(url, params=params, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("controlling_clause")
                logger.warning(f"KruschBiz controlling-clause returned status {res.status_code}: {res.text}")
        except Exception as exc:
            logger.debug(f"KruschBiz connection error: {exc}")
        return None

    # Backwards-compatible alias
    consult_controlling_clause = get_controlling_clause


class KruschLawClient:
    """Client for querying KruschLaw statutory intelligence engine."""

    def __init__(self, base_url: Optional[str] = None, timeout: Optional[float] = None):
        self.base_url = (base_url or settings.LAW_BASE_URL).rstrip("/")
        self.timeout = timeout if timeout is not None else settings.CLIENT_TIMEOUT

    def check_health(self) -> bool:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(f"{self.base_url}/health")
                return res.status_code == 200
        except Exception:
            return False

    def get_controlling_law(
        self,
        doctrine: str,
        city: Optional[str] = None,
        county: Optional[str] = None,
        as_of_date: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Query KruschLaw GET /api/resolver/controlling to resolve governing legal authority."""
        url = f"{self.base_url}/api/resolver/controlling"
        params: Dict[str, Any] = {"doctrine": doctrine}
        if city:
            params["city"] = city
        if county:
            params["county"] = county
        if as_of_date:
            params["as_of_date"] = as_of_date

        headers = {}
        if settings.API_KEY:
            headers["X-API-Key"] = settings.API_KEY

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(url, params=params, headers=headers)
                if res.status_code == 200:
                    return res.json()
                logger.warning(f"KruschLaw resolver returned status {res.status_code}: {res.text}")
        except Exception as exc:
            logger.debug(f"KruschLaw connection error: {exc}")
        return None

    # Backwards-compatible alias
    def query_statute_precedence(
        self,
        doctrine: str,
        jurisdiction: str,
        as_of_date: str
    ) -> Optional[Dict[str, Any]]:
        city = None
        if ":" in jurisdiction:
            parts = jurisdiction.split(":", 1)
            city = parts[1]
        return self.get_controlling_law(doctrine=doctrine, city=city, as_of_date=as_of_date)
