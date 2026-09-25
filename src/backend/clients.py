"""
src/backend/clients.py
======================
Service Client Adapters for KruschBiz and KruschLaw.
Enables KruschBizLaw to communicate with running fleet nodes:
  - KruschBiz (127.0.0.1:8086): Commercial contract precedence & clause extraction
  - KruschLaw (127.0.0.1:8085): Statutory authority graph & legal RAG
Includes graceful fallbacks for local standalone operation and testing.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Any, Dict, Optional
import httpx

logger = logging.getLogger("kruschbizlaw.clients")

BIZ_DEFAULT_URL = "http://127.0.0.1:8086"
LAW_DEFAULT_URL = "http://127.0.0.1:8085"


class KruschBizClient:
    """Client for querying KruschBiz commercial contract engine."""

    def __init__(self, base_url: str = BIZ_DEFAULT_URL, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def check_health(self) -> bool:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(f"{self.base_url}/health")
                return res.status_code == 200
        except Exception:
            return False

    def consult_controlling_clause(
        self,
        counterparty: str,
        topic: str,
        as_of_date: str,
        tenant_id: str = "org_default"
    ) -> Optional[Dict[str, Any]]:
        """Query KruschBiz POST /api/consult to resolve the controlling clause."""
        url = f"{self.base_url}/api/consult"
        payload = {
            "counterparty": counterparty,
            "topic": topic,
            "as_of_date": as_of_date
        }
        headers = {"X-Tenant-ID": tenant_id}
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("controlling_clause")
                logger.warning(f"KruschBiz consult returned status {res.status_code}: {res.text}")
        except Exception as exc:
            logger.debug(f"KruschBiz connection error: {exc}")
        return None


class KruschLawClient:
    """Client for querying KruschLaw statutory intelligence engine."""

    def __init__(self, base_url: str = LAW_DEFAULT_URL, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def check_health(self) -> bool:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(f"{self.base_url}/health")
                return res.status_code == 200
        except Exception:
            return False

    def query_statute_precedence(
        self,
        doctrine: str,
        jurisdiction: str,
        as_of_date: str
    ) -> Optional[Dict[str, Any]]:
        """Query KruschLaw statutory precedence endpoint."""
        url = f"{self.base_url}/api/statutes/precedence"
        params = {
            "query": doctrine,
            "jurisdiction": jurisdiction,
            "as_of_date": as_of_date
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(url, params=params)
                if res.status_code == 200:
                    return res.json()
        except Exception as exc:
            logger.debug(f"KruschLaw connection error: {exc}")
        return None
