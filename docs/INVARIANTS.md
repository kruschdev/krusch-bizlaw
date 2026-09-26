# 🛡️ KruschBizLaw Core Invariants & Pass/Fail Test Matrix

> **Authoritative Specification**: This document establishes the non-negotiable architectural invariants of KruschBizLaw ("The Join"). Every invariant is paired with deterministic, pass/fail automated regression tests.

---

## 📋 The Invariants Matrix

| # | Invariant Name | Failure Mode if Violated | Enforcing Test(s) | Status |
|---|---|---|---|---|
| **INV-1** | **Mandatory As-Of Date (No Silent "Today")** | Unanchored evaluations default to current system timestamp, misapplying future or past laws | `tests/test_invariants.py::TestKruschBizLawInvariants::test_inv_01_mandatory_as_of_date`<br>`tests/test_api.py::test_missing_as_of_date_rejected` | ✅ PASS |
| **INV-2** | **Deterministic Slot Evaluation Over LLMs** | LLM semantic similarity misjudges numerical thresholds (e.g. 1.001 months vs 1.0 ceiling) | `tests/test_invariants.py::TestKruschBizLawInvariants::test_inv_02_deterministic_slot_evaluation`<br>`tests/unit/test_join_properties.py::test_property_deposit_cap_mutation` | ✅ PASS |
| **INV-3** | **AB 12 Temporal Boundary Gating** | 2.0-month deposit demanded prior to July 1, 2024 wrongly marked void, or demanded post-enactment marked valid | `tests/test_invariants.py::TestKruschBizLawInvariants::test_inv_03_ab12_temporal_boundary_gating`<br>`tests/unit/test_join_properties.py::test_property_temporal_boundary_mutation` | ✅ PASS |
| **INV-4** | **Commercial Lease Freedom of Contract** | Commercial lease deposits wrongly subjected to residential AB 12 1-month statutory ceiling | `tests/test_invariants.py::TestKruschBizLawInvariants::test_inv_04_commercial_lease_freedom_of_contract`<br>`tests/unit/test_join_properties.py::test_property_commercial_lease_mutation` | ✅ PASS |
| **INV-5** | **Non-Waivable Public Policy Void Gating** | Contract disclaimers waiving habitability (§ 1942.1) or retaliation defense (§ 1942.5(h)) enforced | `tests/test_invariants.py::TestKruschBizLawInvariants::test_inv_05_non_waivable_public_policy_void_gating`<br>`tests/test_join_engine.py` | ✅ PASS |
| **INV-6** | **Fail-Closed Coverage Hole Handling** | Missing contract terms or unindexed statutory doctrines emit false-positive "compliant" verdicts | `tests/test_invariants.py::TestKruschBizLawInvariants::test_inv_06_fail_closed_coverage_hole_handling`<br>`tests/test_join_engine.py::test_coverage_gap` | ✅ PASS |
| **INV-7** | **Generous Term Recognition (Floors vs Ceilings)** | Exceeding a minimum floor (e.g. 48 hr notice vs 24 hr) wrongly flagged as non-compliant | `tests/test_invariants.py::TestKruschBizLawInvariants::test_inv_07_generous_term_recognition`<br>`tests/unit/test_join_properties.py` | ✅ PASS |
| **INV-8** | **Strict Loopback Data Residency** | Join engine binds externally (0.0.0.0) or communicates across unverified public networks | `tests/test_invariants.py::TestKruschBizLawInvariants::test_inv_08_strict_loopback_data_residency`<br>`tests/test_security_hardening.py` | ✅ PASS |
| **INV-9** | **Resilient Air-Gapped Fleet Federation** | Disconnection or timeout from KruschBiz (8086) or KruschLaw (8085) causes crash cascade | `tests/test_invariants.py::TestKruschBizLawInvariants::test_inv_09_resilient_air_gapped_fleet_federation`<br>`tests/test_api.py::test_health` | ✅ PASS |
| **INV-10** | **Trace & Audit Immutability** | Compliance findings lack unique cryptographic provenance or fail to record partial coverage | `tests/test_invariants.py::TestKruschBizLawInvariants::test_inv_10_trace_and_audit_immutability` | ✅ PASS |

---

## 🔍 Detailed Invariant Specifications

### INV-1: Mandatory As-Of Date (No Silent "Today")
* **Requirement**: Every compliance evaluation endpoint (`/api/conflicts/contract-vs-statute`, `/api/evaluate/clause`) strictly requires `as_of_date` formatted as `YYYY-MM-DD`.
* **Behavior**: Missing, blank, whitespace-only, or improperly formatted dates immediately return `HTTP 400 Bad Request` or `HTTP 422 Unprocessable Entity`. Silent defaulting to `datetime.now()` or `date.today()` is prohibited.
* **Verification Command**:
  ```bash
  pytest tests/test_invariants.py -k "test_inv_01_mandatory_as_of_date"
  ```

### INV-2: Deterministic Slot Evaluation Over Probabilistic LLMs
* **Requirement**: Monetary caps, notice windows, interest percentages, and return timelines are compared via deterministic arithmetic (`float(contract_val) > stat_cap` or `< stat_min`).
* **Behavior**: LLM semantic similarity is never used to confirm numerical compliance. Boundary conditions (e.g. 1.001 months vs 1.0 ceiling) trigger deterministic `VOID_AS_AGAINST_PUBLIC_POLICY`.
* **Verification Command**:
  ```bash
  pytest tests/test_invariants.py -k "test_inv_02_deterministic_slot_evaluation"
  ```

### INV-3: AB 12 Temporal Boundary Gating
* **Requirement**: Evaluates Cal. Civ. Code § 1950.5 under the historical 2.0-month ceiling prior to July 1, 2024, and under the 1.0-month ceiling on and after July 1, 2024.
* **Behavior**:
  - Inquiries with `as_of_date < 2024-07-01` evaluate against 2.0 months unfurnished rent cap.
  - Inquiries with `as_of_date >= 2024-07-01` evaluate against AB 12's 1.0 month rent cap.
* **Verification Command**:
  ```bash
  pytest tests/test_invariants.py -k "test_inv_03_ab12_temporal_boundary_gating"
  ```

### INV-4: Commercial Lease Freedom of Contract
* **Requirement**: Commercial leases are governed by Cal. Civ. Code § 1950.7(f) rather than residential statutory protections.
* **Behavior**: When `property_type='commercial'` or `topic='COMMERCIAL_SECURITY_DEPOSIT'`, freedom of contract applies and statutory 1-month residential caps under AB 12 do not void contractual terms.
* **Verification Command**:
  ```bash
  pytest tests/test_invariants.py -k "test_inv_04_commercial_lease_freedom_of_contract"
  ```

### INV-5: Non-Waivable Public Policy Prohibition Gating
* **Requirement**: Statutory prohibitions against tenant rights waivers must be enforced deterministically.
* **Behavior**: Any contract clause attempting to waive habitability remedies (Cal. Civ. Code § 1942.1) or retaliation defense rights (Cal. Civ. Code § 1942.5(h)) is strictly marked `contract_less_than_mandatory` and `VOID_AS_AGAINST_PUBLIC_POLICY`.
* **Verification Command**:
  ```bash
  pytest tests/test_invariants.py -k "test_inv_05_non_waivable_public_policy_void_gating"
  ```

### INV-6: Fail-Closed Coverage Hole Handling
* **Requirement**: When either a contractual clause or statutory mandate is missing from the record, the engine must never falsely report full compliance.
* **Behavior**: Missing provisions or unindexed legal doctrines return `coverage_gap` with `enforceability=UNSPECIFIED` and `coverage="partial"`.
* **Verification Command**:
  ```bash
  pytest tests/test_invariants.py -k "test_inv_06_fail_closed_coverage_hole_handling"
  ```

### INV-7: Generous Term Recognition (Floors vs Ceilings)
* **Requirement**: Distinguishes statutory floors (where exceeding is legal) from statutory ceilings (where exceeding is illegal).
* **Behavior**:
  - Exceeding a minimum floor (e.g. 48 hours landlord notice vs 24-hr statutory minimum under § 1954) renders `contract_more_generous` and `ENFORCEABLE`.
  - Exceeding a maximum ceiling (e.g. 45 days deposit return vs 21-day statutory ceiling under § 1950.5(g)(1)) renders `contract_less_than_mandatory` and `VOID_AS_AGAINST_PUBLIC_POLICY`.
* **Verification Command**:
  ```bash
  pytest tests/test_invariants.py -k "test_inv_07_generous_term_recognition"
  ```

### INV-8: Strict Loopback Data Residency
* **Requirement**: KruschBizLaw services and client adapters must bind and communicate strictly across loopback interfaces.
* **Behavior**: Service binds to `127.0.0.1:8087` by default. Wildcard binding (`0.0.0.0`) is prohibited unless `ALLOW_LAN=1` is explicitly set. In production mode, binding outside loopback triggers a startup fatal exception.
* **Verification Command**:
  ```bash
  pytest tests/test_security_hardening.py
  ```

### INV-9: Resilient Air-Gapped Fleet Federation
* **Requirement**: Fleet adapters to KruschBiz (`127.0.0.1:8086`) and KruschLaw (`127.0.0.1:8085`) must operate asynchronously and degrade gracefully.
* **Behavior**: If either peer service is offline, queries return `None` without unhandled exceptions or crash cascades, allowing KruschBizLaw to continue functioning in standalone mode.
* **Verification Command**:
  ```bash
  pytest tests/test_invariants.py -k "test_inv_09_resilient_air_gapped_fleet_federation"
  ```

### INV-10: Trace & Audit Immutability
* **Requirement**: Every cross-examination evaluation must produce a unique, immutable audit trace.
* **Behavior**: Each `ComplianceFinding` receives a cryptographically unique `trace_id` prefixed with `trace_bizlaw_` and records `coverage: partial` for audit trail provenance.
* **Verification Command**:
  ```bash
  pytest tests/test_invariants.py -k "test_inv_10_trace_and_audit_immutability"
  ```
