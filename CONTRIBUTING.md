# 🤝 Contributing to KruschBizLaw

Welcome, and thank you for contributing to KruschBizLaw!

KruschBizLaw is the sovereign cross-domain statutory compliance engine ("The Join") unifying commercial contract terms from KruschBiz and non-waivable statutory authorities from KruschLaw. All contributions must uphold our non-negotiable architectural invariants.

---

## 🏛️ Core Principles & Invariant Boundaries

1. **Air-Gap Compliance (Zero External Cloud I/O)**:
   - KruschBizLaw never makes outbound calls to public cloud APIs, hosted LLM endpoints, or external telemetry trackers.
   - All fleet services run locally on loopback (`127.0.0.1` / `::1`).
2. **Mandatory As-Of Date (INV-1)**:
   - All evaluation requests must explicitly supply `as_of_date` formatted as `YYYY-MM-DD`. No silent defaulting to "today".
3. **Deterministic Arithmetic Over LLMs (INV-2)**:
   - Numerical thresholds (rent caps, notice hours, return days, interest percentages) are evaluated deterministically via typed float/int arithmetic, never LLM semantic similarity.
4. **Temporal Boundary Gating (INV-3)**:
   - Temporal amendments (e.g. California AB 12 1-month security deposit cap taking effect July 1, 2024) must strictly separate past compliant leases from modern violations.
5. **Commercial Lease Freedom of Contract (INV-4)**:
   - Cal. Civ. Code § 1950.7(f) permissive waiver permits commercial leases to set deposit terms freely without triggering residential AB 12 violations.
6. **Non-Waivable Public Policy Void Gating (INV-5)**:
   - Disclaimers purporting to waive habitability (§ 1942.1) or retaliation defense (§ 1942.5(h)) are deterministically ruled `VOID_AS_AGAINST_PUBLIC_POLICY`.
7. **Fail-Closed Coverage Hole Handling (INV-6)**:
   - Missing contractual provisions or unmapped legal doctrines return explicit `coverage_gap` with `enforceability=UNSPECIFIED`.
8. **Strict Loopback Data Residency (INV-8)**:
   - Engine and client adapters bind strictly to `127.0.0.1` and reject non-loopback bindings in production.

---

## 🛠️ Local Development Setup

### 1. Environment Setup
```bash
git clone https://github.com/kruschdev/krusch-bizlaw.git
cd krusch-bizlaw
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 2. Launch FastAPI Backend Server (Port 8087)
```bash
python3 -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8087
```

### 3. Launch Streamlit Web UI (Port 8507)
```bash
streamlit run src/frontend/app.py --server.port 8507 --server.address 127.0.0.1
```

### 4. Run the 60-Second Headless Demo
```bash
python3 scripts/demo_60s.py
```
Executes all 6 core cross-domain join checks in <0.01 seconds with zero external dependencies.

---

## 🧪 Verification & Test Suite

Before opening a pull request, all automated test batteries must pass cleanly:

```bash
# 1. Run full pytest suite (43+ tests)
pytest tests -v

# 2. Run property-based mutation tests
pytest tests/unit/test_join_properties.py -v

# 3. Run invariants test suite
pytest tests/test_invariants.py -v

# 4. Run benchmark gate (11/11 scenarios)
python3 scripts/eval_benchmark.py
```

---

## 📋 Pull Request Checklist

When submitting a pull request, ensure:
1. `docs/INVARIANTS.md` matrix is updated if any new invariant is introduced.
2. 100% of tests pass cleanly.
3. No external cloud API calls or unauthenticated outbound dependencies are added.
4. Conventional commit messages (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`).
