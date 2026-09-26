# 📓 Changelog

All notable changes to **KruschBizLaw** are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] - 2026-09-25

### 🚀 Added
- **Authoritative Invariants Specification**: Published `docs/INVARIANTS.md` formalizing the 10 Core Architectural Invariants with automated pass/fail regression test commands.
- **60-Second Zero-Dependency Headless Runner**: Added `scripts/demo_60s.py` executing 6 core contract-vs-statute join scenarios (pre/post-AB 12, commercial lease freedom of contract, statutory floors, non-waivable public policy waivers, coverage holes) in under 0.01 seconds without external dependencies.
- **Property-Based Mutation Test Suite**: Published `tests/unit/test_join_properties.py` verifying that parameter mutations across statutory thresholds, temporal boundaries, property types, and syntax variants deterministically flip or maintain legal verdicts.
- **Invariants Test Suite**: Published `tests/test_invariants.py` enforcing INV-1 through INV-10 across API and engine surfaces.
- **Security Hardening & Strict Loopback Data Residency**: Added `src/backend/config.py` with `Settings`, `is_strict_loopback()`, `is_loopback_or_private_host()`, and `validate_security_invariants()` enforcing loopback binding (`127.0.0.1:8087`) and mandatory API keys outside development.
- **Security Test Suite**: Published `tests/test_security_hardening.py` testing strict loopback, private host detection, wildcard binding prevention, and production gating.
- **Fleet Client Hardening**: Updated `src/backend/clients.py` with resilient adapters targeting authoritative REST routes on KruschBiz (`GET /api/resolver/controlling-clause`) and KruschLaw (`GET /api/resolver/controlling`) with graceful fallback to standalone offline mode.
- **Number Word Normalization**: Enhanced `src/engine/join.py` with word-to-digit normalization (`two months` -> `2.0`, `forty-five days` -> `45.0`) for resilient raw clause analysis.
- **Lifespan Security Validation**: Implemented FastAPI `lifespan` in `src/backend/main.py` ensuring security invariants and data residency are verified on startup.
- **Corpus License & Data Provenance**: Published `data/CORPUS_LICENSE.md` certifying public domain California statutory texts and synthetic benchmark contract clauses with zero confidential data.
- **OSS Hygiene**: Published `CONTRIBUTING.md`, `.github/pull_request_template.md`, and `.github/workflows/ci.yml`.

---

## [0.1.0-alpha.1] - 2026-09-25

### 🚀 Added
- Initial release of KruschBizLaw cross-domain statutory compliance platform ("The Join").
- Deterministic contract-vs-statute join evaluation engine (`src/engine/join.py`).
- Non-waivable statutory mandates registry for California tenancies (`src/engine/mandates.py`).
- 11-scenario adversarial benchmark suite with sub-millisecond execution (`scripts/eval_benchmark.py`).
- FastAPI REST API (`src/backend/main.py`) on port 8087.
- Cyber-executive Streamlit UI (`src/frontend/app.py`) on port 8507.
