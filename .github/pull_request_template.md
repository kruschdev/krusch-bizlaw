## Description
<!-- Provide a clear, concise summary of the proposed changes and architectural context. -->

## Invariant Conformance & Checklist
- [ ] **Automated Test Suite**: All tests pass cleanly (`pytest tests/`).
- [ ] **Core Invariants Verified**: Passes all tests in `tests/test_invariants.py` (INV-1 through INV-10).
- [ ] **Property-Based Mutations**: Passes property-based test suite (`pytest tests/unit/test_join_properties.py`).
- [ ] **Mandatory As-Of Date**: Verified `as_of_date` is strictly enforced without silent fallbacks.
- [ ] **AB 12 Temporal Gating**: Verified clean separation between pre-2024-07-01 and post-2024-07-01 deposit rules.
- [ ] **Commercial Lease Freedom of Contract**: Commercial leases correctly governed by § 1950.7(f) permissive waiver.
- [ ] **Non-Waivable Public Policy Gate**: Habitability (§ 1942.1) and retaliation (§ 1942.5(h)) waivers deterministically voided.
- [ ] **Fail-Closed Coverage Holes**: Unmapped topics emit `coverage_gap` and `UNSPECIFIED` rather than false "compliant" verdicts.
- [ ] **Strict Loopback Data Residency**: Verified service binds to `127.0.0.1:8087` and rejects external interfaces.
- [ ] **Fleet Resilience**: Verified graceful degradation when KruschBiz (8086) or KruschLaw (8085) are offline.
- [ ] **Headless Demo**: 60-second headless runner passes cleanly (`python3 scripts/demo_60s.py`).
- [ ] **Docs & Invariants Updated**: Updated `docs/INVARIANTS.md` or `CHANGELOG.md` if applicable.

## Related Issues or Specs
<!-- E.g., Implements ORCHESTRATOR_SPEC section 4 -->
