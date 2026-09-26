# ⚖️ KruschBizLaw

> **Sovereign Cross-Domain Statutory Compliance Engine & Contract-vs-Statute Join Platform**  
> *Unifying commercial contract terms from KruschBiz and non-waivable statutory authorities from KruschLaw to execute deterministic legal enforceability cross-examinations ("The Join") without LLM hallucinations.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version: 0.2.0](https://img.shields.io/badge/Version-0.2.0-blue.svg)](CHANGELOG.md)
[![Python 3.11 | 3.12](https://img.shields.io/badge/Python-3.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Tests: 43 Passing](https://img.shields.io/badge/Tests-43%20Passing-brightgreen.svg)](tests/)
[![Invariants: 10/10 Verified](https://img.shields.io/badge/Invariants-10%2F10%20Verified-brightgreen.svg)](docs/INVARIANTS.md)
[![Benchmark: 11/11 (100%)](https://img.shields.io/badge/Benchmark-11%2F11%20(100%25)-brightgreen.svg)](scripts/eval_benchmark.py)

---

## 🏛️ The Three-Pillar Architecture: Why KruschBizLaw?

In high-stakes enterprise governance, conflating commercial contract precedence with statutory legal analysis leads to bloated codebases, prompt token explosion, and brittle reasoning traps. KruschBizLaw implements a strict **Three-Pillar Separation of Concerns**:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. KRUSCH-LAW (Port 8085 / 8505)                            │
│    Sovereign California Statutory Intelligence & Evidentiary│
│    • Precedence DAG: Municipal vs State statutory hierarchy │
│    • Evidentiary Discovery & Bates-stamped grounding        │
│    • Tenant defense checklists & deadline calculations      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. KRUSCH-BIZ (Port 8086 / 8506)                            │
│    Sovereign Corporate Intelligence & Relational Graph      │
│    • Precedence Graph: AMENDS, SUPERSEDES, INCORPORATES     │
│    • Controlling document resolver across historical dates  │
│    • Structured commercial slot extraction (Net Days, Caps) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. KRUSCH-BIZLAW (Port 8087 / 8507) — "THE JOIN"            │
│    Cross-Domain Statutory Compliance & Enforceability       │
│    • Compares contract slots against statutory mandates     │
│    • Detects public policy violations (e.g. AB 12, entry)   │
│    • Output: VOID_AS_AGAINST_PUBLIC_POLICY or ENFORCEABLE   │
└─────────────────────────────────────────────────────────────┘
```

### Keeping Each Engine Lightweight
- **KruschLaw** stays lightweight: Focuses strictly on statutory law, codes, precedents, and litigation evidence.
- **KruschBiz** stays lightweight: Focuses strictly on corporate deal rooms, contract graphs, and commercial terms.
- **KruschBizLaw unifies them**: Serves as the dedicated, deterministic cross-examination bridge evaluating contract slots directly against statutory floors and ceilings.

---

## 🛡️ The 10 Core Architectural Invariants

KruschBizLaw is governed by 10 non-negotiable architectural invariants detailed in **[docs/INVARIANTS.md](docs/INVARIANTS.md)**:

| Invariant | Name | Guarantee |
|---|---|---|
| **INV-1** | **Mandatory As-Of Date** | `as_of_date` is strictly mandatory. No silent defaulting to "today" is permitted. |
| **INV-2** | **Deterministic Slot Evaluation** | Numerical thresholds and caps are evaluated via typed arithmetic, never LLM semantic similarity. |
| **INV-3** | **AB 12 Temporal Boundary Gating** | 2-month deposit is valid pre-2024-07-01; strictly void post-enactment. |
| **INV-4** | **Commercial Lease Freedom of Contract** | Commercial tenancies govern under § 1950.7(f) permissive waiver rather than residential ceilings. |
| **INV-5** | **Non-Waivable Public Policy Gate** | Habitability (§ 1942.1) and retaliation (§ 1942.5(h)) waivers are deterministically voided. |
| **INV-6** | **Fail-Closed Coverage Holes** | Missing provisions or unindexed topics return `coverage_gap` with `UNSPECIFIED` enforceability. |
| **INV-7** | **Generous Term Recognition** | Exceeding minimum floors is `contract_more_generous` and `ENFORCEABLE`. |
| **INV-8** | **Strict Loopback Data Residency** | Service binds to `127.0.0.1:8087`. External interface bindings rejected in production. |
| **INV-9** | **Resilient Fleet Federation** | Client adapters handle disconnection or timeouts from KruschBiz/KruschLaw with graceful fallback. |
| **INV-10** | **Trace & Audit Immutability** | Every finding generates a unique `trace_id` recording `coverage: partial` for audit trail provenance. |

---

## 🚀 Core Capabilities

* ⚖️ **Deterministic Contract-vs-Statute Join ("The Join")**:
  - Rather than delegating compliance analysis to probabilistic LLMs, KruschBizLaw executes deterministic, rule-based slot evaluations.
  - Renders binding legal verdicts:
    - `contract_less_than_mandatory` (`VOID_AS_AGAINST_PUBLIC_POLICY`)
    - `aligned` (`ENFORCEABLE`)
    - `contract_more_generous` (`ENFORCEABLE`)
    - `coverage_gap` (`UNSPECIFIED`)
* 📅 **Mandatory Temporal As-Of Date Traversal**:
  - Enforces the non-negotiable invariant: **No silent "today"**.
  - Accurately switches legal baselines across statutory effective dates (e.g., California AB 12 1-month security deposit cap taking effect on **July 1, 2024**).
* 🏢 **Property Type & Freedom of Contract Routing**:
  - Distinguishes residential tenancies (subject to non-waivable statutory ceilings) from commercial leases (where freedom of contract permits security deposit waivers under Cal. Civ. Code § 1950.7(f)).
* 🛡️ **Fail-Closed Coverage Gap Detection**:
  - Surfaces explicit `coverage_gap` indicators whenever a contractual slot or statutory doctrine is missing from the record, preventing false assurances of compliance.
* 🔌 **Dual Operation Mode (Fleet-Connected or Standalone)**:
  - Operates as a distributed fleet coordinator communicating via REST with KruschBiz (`127.0.0.1:8086`) and KruschLaw (`127.0.0.1:8085`).
  - Operates as a completely self-contained, standalone compliance verification engine for offline air-gapped evaluation.

---

## 📊 11-Scenario Compliance Benchmark Suite

KruschBizLaw is benchmarked against 11 real-world conflict pairs covering residential, commercial, and financial statutory doctrines:

| Benchmark ID | Test Scenario | Controlling Statute | Mandate Type | Deterministic Verdict |
|---|---|---|---|---|
| `TC-01` | **Post-AB 12 Security Deposit Violation** (2.0 mo demanded post-2024-07-01) | Cal. Civ. Code § 1950.5(c)(1) | Statutory Ceiling (1.0 mo) | `contract_less_than_mandatory` (`VOID_AS_AGAINST_PUBLIC_POLICY`) |
| `TC-02` | **Pre-AB 12 Security Deposit Compliance** (2.0 mo demanded pre-2024-07-01) | Cal. Civ. Code § 1950.5(c) (Prior) | Statutory Ceiling (2.0 mo) | `aligned` (`ENFORCEABLE`) |
| `TC-03` | **Sub-Statutory Landlord Entry Notice** (12 hrs vs 24 hr floor) | Cal. Civ. Code § 1954(d)(1) | Statutory Floor (24.0 hrs) | `contract_less_than_mandatory` (`VOID_AS_AGAINST_PUBLIC_POLICY`) |
| `TC-04` | **More Generous Entry Notice** (48 hrs vs 24 hr floor) | Cal. Civ. Code § 1954(d)(1) | Statutory Floor (24.0 hrs) | `contract_more_generous` (`ENFORCEABLE`) |
| `TC-05` | **Extended Deposit Return Timeline** (45 days vs 21-day ceiling) | Cal. Civ. Code § 1950.5(g)(1) | Statutory Ceiling (21 days) | `contract_less_than_mandatory` (`VOID_AS_AGAINST_PUBLIC_POLICY`) |
| `TC-06` | **Expedited Deposit Return Timeline** (14 days vs 21-day ceiling) | Cal. Civ. Code § 1950.5(g)(1) | Statutory Ceiling (21 days) | `contract_more_generous` (`ENFORCEABLE`) |
| `TC-07` | **Prohibited Habitability Waiver** (repair-and-deduct disclaimer) | Cal. Civ. Code § 1942.1 | Statutory Prohibition | `contract_less_than_mandatory` (`VOID_AS_AGAINST_PUBLIC_POLICY`) |
| `TC-08` | **Prohibited Retaliation Waiver** (retaliation defense disclaimer) | Cal. Civ. Code § 1942.5(h) | Statutory Prohibition | `contract_less_than_mandatory` (`VOID_AS_AGAINST_PUBLIC_POLICY`) |
| `TC-09` | **Excessive Late Fee Liquidated Damages** (15% vs 5% ceiling) | Cal. Civ. Code § 1671(d) | Statutory Ceiling (5.0%) | `contract_less_than_mandatory` (`VOID_AS_AGAINST_PUBLIC_POLICY`) |
| `TC-10` | **Commercial Lease Deposit Flexibility** (3.0 mo base rent) | Cal. Civ. Code § 1950.7(f) | Permissive Waiver | `aligned` (`ENFORCEABLE`) |
| `TC-11` | **Untracked Statutory Topic Coverage Gap** (`MUNICIPAL_SIDEWALK`) | None (Corpus Hole) | Coverage Gap | `coverage_gap` (`UNSPECIFIED`) |

---

## ⚡ Quickstart

### 1. Run 60-Second Headless Demo (<0.01s Execution)
```bash
python3 scripts/demo_60s.py
```

### 2. Launch FastAPI Backend Server (Port 8087)
```bash
python3 -m uvicorn src.backend.main:app --host 127.0.0.1 --port 8087
```

### 3. Launch Streamlit Web UI (Port 8507)
```bash
streamlit run src/frontend/app.py --server.port 8507 --server.address 127.0.0.1
```

### 4. Run Benchmark Suite
```bash
python3 scripts/eval_benchmark.py
```

### 5. Run Automated Pytest Suite (43+ Tests)
```bash
pytest tests -v
```

---

## 🌐 API Reference

* `POST /api/conflicts/contract-vs-statute`: Primary cross-examination between contract slots and statutory mandates.
* `POST /api/evaluate/clause`: Direct evaluation of raw clause strings against statutory baselines.
* `GET /api/mandates`: Enumerate registered statutory floors, ceilings, and prohibitions.
* `GET /health`: Inspect service health, loopback residency, and fleet connectivity to KruschBiz and KruschLaw.

---

## 📜 Compliance, Provenance & Licensing

* **[docs/INVARIANTS.md](docs/INVARIANTS.md)**: Formal specification of INV-1 through INV-10 and regression test matrix.
* **[data/CORPUS_LICENSE.md](data/CORPUS_LICENSE.md)**: Public domain statutory data provenance and synthetic evaluation licensing.
* **[CHANGELOG.md](CHANGELOG.md)**: Chronological record of architectural enhancements.
* **[CONTRIBUTING.md](CONTRIBUTING.md)**: Guidelines for contributing code and invariants.
* KruschBizLaw is open-source software licensed under the **[MIT License](LICENSE)**.
