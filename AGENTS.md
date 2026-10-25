# KruschBizLaw (`krusch-bizlaw`) — Agent Guidelines & Architecture (v0.9.0)

> **Status**: Production Cross-Domain Statutory Compliance & Contract-vs-Statute Join Engine  
> **Version**: 0.9.0  
> **Tests**: 64 Passing (`pytest` — 100% green across 17 statutory mandates in CA, DE, NY, TX, and Federal)  
> **Ports**: Backend API `:8087` | Streamlit Compliance Workbench `:8507`  
> **Last updated**: 2026-10-18

---

## 1. System Architecture

`krusch-bizlaw` executes **The Join** between corporate contractual provisions (`krusch-biz`) and binding statutory floors/ceilings (`krusch-law` + `krusch-authority-packs`).
- **Backend API**: FastAPI (`src/backend/main.py`) on `127.0.0.1:8087`
- **Compliance Engine**: Evaluates extracted contract slots (e.g., late fee percentages, liability caps, non-compete clauses, commercial lease remedies, Delaware DGCL § 102(b)(7) exculpation, NY GOL § 5-1401 choice-of-law, TX Bus. & Com. Code § 15.50, Federal UCC / 11 U.S.C. § 365(e) ipso facto clauses) against statutory mandates as of a target `as_of_date`.
- **Frontend UI**: Streamlit workbench (`src/frontend/app.py`) on `127.0.0.1:8507`
- **Gateway Integration**: Exposed via `check_compliance` on `krusch-gateway-mcp`.

---

## 2. Verification & Testing

Run the full compliance test suite:
```bash
PYTHONPATH=. ../krusch-law/venv/bin/pytest tests/ -v
```
