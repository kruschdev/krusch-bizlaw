"""
tests/test_api.py
=================
Integration tests for KruschBizLaw FastAPI REST API.
"""

from fastapi.testclient import TestClient
from src.backend.main import app

client = TestClient(app)


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["service"] == "krusch-bizlaw"
    assert "fleet_connectivity" in data


def test_list_mandates():
    res = client.get("/api/mandates")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 8
    assert "SECURITY_DEPOSIT" in data["mandates"]


def test_evaluate_compliance_endpoint():
    payload = {
        "as_of_date": "2024-08-01",
        "jurisdiction": "CA:Oakland",
        "topics": ["SECURITY_DEPOSIT", "ENTRY_NOTICE"],
        "contract_slots": {
            "deposit_cap_months": 2.0,
            "entry_notice_hours": 12.0
        }
    }
    res = client.post("/api/conflicts/contract-vs-statute", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["verdict"] == "NON_COMPLIANT_TERMS_FOUND"
    assert len(data["findings"]) == 2
    assert data["summary"]["non_compliant"] == 2


def test_evaluate_single_clause():
    params = {
        "topic": "ENTRY_NOTICE",
        "as_of_date": "2024-08-01",
        "clause_text": "Landlord shall provide 12 hours advance written notice."
    }
    res = client.post("/api/evaluate/clause", params=params)
    assert res.status_code == 200
    data = res.json()
    assert data["alignment"] == "contract_less_than_mandatory"
    assert data["enforceability"] == "VOID_AS_AGAINST_PUBLIC_POLICY"


def test_missing_as_of_date_rejected():
    payload = {
        "jurisdiction": "CA:Oakland",
        "topics": ["SECURITY_DEPOSIT"],
        "as_of_date": ""
    }
    res = client.post("/api/conflicts/contract-vs-statute", json=payload)
    assert res.status_code == 400
    assert "as_of_date" in res.json()["detail"]
