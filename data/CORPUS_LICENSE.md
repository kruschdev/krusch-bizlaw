# 📜 Evaluation Corpus License & Data Provenance

> **Authoritative Compliance Statement**: This document defines the legal provenance, copyright status, and usage licensing for all statutory mandates, evaluation fixtures, and benchmark pairs bundled within KruschBizLaw.

---

## 1. Provenance Classifications

All statutory texts, non-waivable rules, and evaluation fixtures in `data/` and `src/engine/mandates.py` belong to one of two strictly documented, non-confidential categories:

### Category A: Public Domain California & Municipal Statutory Mandates
- **Source**:
  - California State Legislature (California Civil Code §§ 1671(d), 1942.1, 1942.5(h), 1950.5, 1950.7, 1954, and California Constitution Art. XV § 1).
- **Legal Status**:
  - Government edicts, state legislative statutes, and public codes are in the public domain and not subject to copyright under U.S. law (*Georgia v. Public.Resource.Org, Inc.*, 140 S. Ct. 1498 (2020)).
- **Fair Use & Reproduction**:
  - Codified and evaluated under 17 U.S.C. § 107 for automated legal informatics research, statutory compliance verification, and software benchmarking.
- **Privacy Policy**:
  - Zero private tenant or commercial confidential data is included.

### Category B: Synthetic Adversarial Fixtures & Benchmark Pairs
- **Source**:
  - 100% synthetically authored by the Krusch engineering team specifically designed to test cross-domain contract-vs-statute compliance edge cases (`scripts/eval_benchmark.py`, `tests/unit/test_join_properties.py`).
- **Composition**:
  - Synthetic lease and agreement provisions (e.g. 2.0-month deposit clauses, 12-hour entry provisions, 45-day deposit return schedules, 15% late charge penalties).
  - Designed specifically to test temporal gating (pre- vs post-AB 12), commercial lease freedom of contract (§ 1950.7(f)), statutory floor generosity, and fail-closed coverage hole handling.
- **Licensing**:
  - Released under the **Creative Commons Attribution 4.0 International (CC-BY-4.0)** license and dual-licensed under the **MIT License**.

---

## 2. Zero Confidential Client Data Warranty

The authors of KruschBizLaw warrant that:
1. **Zero Client Data**: No confidential corporate agreements, deal room secrets, attorney-client privileged communications, or private tenant records are stored in this repository.
2. **Deterministic Reproducibility**: Open-source contributors, corporate counsel, and compliance teams can freely clone, execute, inspect, and redistribute the benchmark fixtures without intellectual property infringement or regulatory liability.
