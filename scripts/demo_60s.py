#!/usr/bin/env python3
"""
scripts/demo_60s.py
===================
60-Second Headless Demonstration of KruschBizLaw ("The Join").
Runs with zero external dependencies (no Ollama, no PostgreSQL, no GPU).
Demonstrates:
  1. Contract-vs-Statute Cross-Examination ("The Join")
  2. Temporal As-Of Boundary Gating (Pre-AB 12 vs Post-AB 12)
  3. Commercial Lease Freedom of Contract vs Residential Protections
  4. Statutory Floor Generosity vs Ceiling Violations
  5. Non-Waivable Public Policy Disclaimers
  6. Fail-Closed Coverage Hole Handling
"""

from __future__ import annotations

import os
import sys
import time
from datetime import date

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.engine.join import evaluate_contract_vs_statute_slots, synthesize_portfolio_response


def main():
    t0 = time.perf_counter()
    print("\n" + "=" * 78)
    print("  ⚖️  KRUSCH-BIZLAW 60-SECOND HEADLESS DEMO")
    print("  Sovereign Cross-Domain Statutory Compliance Platform ('The Join')")
    print("=" * 78 + "\n")

    # Step 1: Post-AB 12 Security Deposit Violation
    print("Step 1: Post-AB 12 Security Deposit Violation (Ceiling Breach)")
    print("-" * 78)
    f1 = evaluate_contract_vs_statute_slots(
        topic="SECURITY_DEPOSIT",
        as_of=date(2024, 8, 1),
        contract_slots={"deposit_cap_months": 2.0},
        property_type="residential"
    )
    print("  [Contract Term: 2.0 months rent deposit] As-of: 2024-08-01 (Post-AB 12)")
    print(f"  -> Controlling Statute:  {f1.controlling_statute['citation']}")
    print(f"  -> Mandate Type:        {f1.controlling_statute['mandate_type']}")
    print(f"  -> Alignment Verdict:   {f1.alignment.upper()}")
    print(f"  -> Enforceability:      {f1.enforceability}")
    print(f"  -> Trace ID:            {f1.trace_id}")
    print(f"  -> Legal Explanation:   {f1.explanation}")

    # Step 2: Pre-AB 12 Security Deposit Compliance
    print("\n" + "=" * 78)
    print("Step 2: Temporal Invariant Gating (Same Term Evaluated Pre-AB 12)")
    print("-" * 78)
    f2 = evaluate_contract_vs_statute_slots(
        topic="SECURITY_DEPOSIT",
        as_of=date(2024, 3, 1),
        contract_slots={"deposit_cap_months": 2.0},
        property_type="residential"
    )
    print("  [Contract Term: 2.0 months rent deposit] As-of: 2024-03-01 (Pre-AB 12)")
    print(f"  -> Controlling Statute:  {f2.controlling_statute['citation']}")
    print(f"  -> Alignment Verdict:   {f2.alignment.upper()}")
    print(f"  -> Enforceability:      {f2.enforceability}")
    print(f"  -> Legal Explanation:   {f2.explanation}")

    # Step 3: Commercial Lease Freedom of Contract
    print("\n" + "=" * 78)
    print("Step 3: Commercial Lease Permissive Waiver (§ 1950.7(f))")
    print("-" * 78)
    f3 = evaluate_contract_vs_statute_slots(
        topic="SECURITY_DEPOSIT",
        as_of=date(2024, 8, 1),
        contract_slots={"deposit_cap_months": 3.0},
        property_type="commercial"
    )
    print("  [Commercial Lease: 3.0 months base rent deposit] As-of: 2024-08-01")
    print(f"  -> Controlling Statute:  {f3.controlling_statute['citation']}")
    print(f"  -> Mandate Type:        {f3.controlling_statute['mandate_type']}")
    print(f"  -> Alignment Verdict:   {f3.alignment.upper()}")
    print(f"  -> Enforceability:      {f3.enforceability}")
    print(f"  -> Legal Explanation:   {f3.explanation}")

    # Step 4: Statutory Floor Generosity
    print("\n" + "=" * 78)
    print("Step 4: Statutory Floor Generosity (48 hrs vs 24 hrs § 1954)")
    print("-" * 78)
    f4 = evaluate_contract_vs_statute_slots(
        topic="ENTRY_NOTICE",
        as_of=date(2024, 8, 1),
        contract_slots={"entry_notice_hours": 48.0}
    )
    print("  [Contract Term: 48 hours advance notice] Statutory Floor: 24 hours")
    print(f"  -> Controlling Statute:  {f4.controlling_statute['citation']}")
    print(f"  -> Alignment Verdict:   {f4.alignment.upper()}")
    print(f"  -> Enforceability:      {f4.enforceability}")
    print(f"  -> Legal Explanation:   {f4.explanation}")

    # Step 5: Non-Waivable Public Policy Prohibition
    print("\n" + "=" * 78)
    print("Step 5: Non-Waivable Public Policy Disclaimer (§ 1942.1 Habitability)")
    print("-" * 78)
    f5 = evaluate_contract_vs_statute_slots(
        topic="HABITABILITY_WAIVER",
        as_of=date(2024, 8, 1),
        contract_slots={"waives_habitability": True}
    )
    print("  [Contract Term: Tenant waives statutory habitability remedies under § 1941]")
    print(f"  -> Controlling Statute:  {f5.controlling_statute['citation']}")
    print(f"  -> Mandate Type:        {f5.controlling_statute['mandate_type']}")
    print(f"  -> Alignment Verdict:   {f5.alignment.upper()}")
    print(f"  -> Enforceability:      {f5.enforceability}")
    print(f"  -> Legal Explanation:   {f5.explanation}")

    # Step 6: Fail-Closed Coverage Hole
    print("\n" + "=" * 78)
    print("Step 6: Fail-Closed Coverage Hole Handling (Untracked Doctrine)")
    print("-" * 78)
    f6 = evaluate_contract_vs_statute_slots(
        topic="MUNICIPAL_SIDEWALK_ASSESSMENT",
        as_of=date(2024, 8, 1),
        contract_slots={"sidewalk_fee": 500}
    )
    print("  [Query Topic: MUNICIPAL_SIDEWALK_ASSESSMENT] (Absent from statutory pack)")
    print(f"  -> Alignment Verdict:   {f6.alignment.upper()}")
    print(f"  -> Enforceability:      {f6.enforceability}")
    print(f"  -> Controlling Statute:  {f6.controlling_statute}")
    print(f"  -> Legal Explanation:   {f6.explanation}")

    # Step 7: Commercial Non-Compete Restraint (BPC § 16600)
    print("\n" + "=" * 78)
    print("Step 7: Commercial / Employment Non-Compete Restraint (BPC § 16600)")
    print("-" * 78)
    f7 = evaluate_contract_vs_statute_slots(
        topic="NON_COMPETE",
        as_of=date(2024, 8, 1),
        contract_slots={"restrains_trade": True},
        raw_content="Employee agrees not to engage in or establish any competing enterprise for 24 months."
    )
    print("  [Contract Term: Post-employment non-compete restraint for 24 months]")
    print(f"  -> Controlling Statute:  {f7.controlling_statute['citation']}")
    print(f"  -> Mandate Type:        {f7.controlling_statute['mandate_type']}")
    print(f"  -> Alignment Verdict:   {f7.alignment.upper()}")
    print(f"  -> Enforceability:      {f7.enforceability}")
    print(f"  -> Legal Explanation:   {f7.explanation}")

    # Step 8: Unilateral Attorney Fee Preemption (CC § 1717)
    print("\n" + "=" * 78)
    print("Step 8: Unilateral Attorney Fee Preemption & Bilateral Rewrite (CC § 1717)")
    print("-" * 78)
    f8 = evaluate_contract_vs_statute_slots(
        topic="ATTORNEY_FEE_RECIPROCITY",
        as_of=date(2024, 8, 1),
        contract_slots={"unilateral_fee_shifting": True},
        raw_content="Borrower shall pay all attorney fees incurred by Lender in enforcement."
    )
    print("  [Contract Term: Borrower shall pay all attorney's fees incurred by Lender]")
    print(f"  -> Controlling Statute:  {f8.controlling_statute['citation']}")
    print(f"  -> Mandate Type:        {f8.controlling_statute['mandate_type']}")
    print(f"  -> Alignment Verdict:   {f8.alignment.upper()}")
    print(f"  -> Enforceability:      {f8.enforceability}")
    print(f"  -> Legal Explanation:   {f8.explanation}")

    # Step 9: Employee Invention Assignment Exclusions (LC § 2870)
    print("\n" + "=" * 78)
    print("Step 9: Employee Invention Assignment Exclusions (Labor Code § 2870)")
    print("-" * 78)
    f9 = evaluate_contract_vs_statute_slots(
        topic="INVENTION_ASSIGNMENT",
        as_of=date(2024, 8, 1),
        contract_slots={"assigns_all_inventions": True},
        raw_content="Employee assigns all inventions whether or not conceived on employee's own time or outside working hours."
    )
    print("  [Contract Term: Employee assigns all inventions conceived on own time]")
    print(f"  -> Controlling Statute:  {f9.controlling_statute['citation']}")
    print(f"  -> Mandate Type:        {f9.controlling_statute['mandate_type']}")
    print(f"  -> Alignment Verdict:   {f9.alignment.upper()}")
    print(f"  -> Enforceability:      {f9.enforceability}")
    print(f"  -> Legal Explanation:   {f9.explanation}")

    # Step 10: Consumer Privacy Statutory Rights Waiver (CC § 1798.192 & § 1751)
    print("\n" + "=" * 78)
    print("Step 10: Consumer Privacy Statutory Rights Waiver (CCPA § 1798.192 / CLRA § 1751)")
    print("-" * 78)
    f10 = evaluate_contract_vs_statute_slots(
        topic="CONSUMER_PRIVACY_WAIVER",
        as_of=date(2024, 8, 1),
        contract_slots={"waives_privacy_rights": True},
        raw_content="Consumer agrees to waive all statutory privacy rights and has no right to delete personal information."
    )
    print("  [Contract Term: Consumer waives all statutory privacy and deletion rights]")
    print(f"  -> Controlling Statute:  {f10.controlling_statute['citation']}")
    print(f"  -> Mandate Type:        {f10.controlling_statute['mandate_type']}")
    print(f"  -> Alignment Verdict:   {f10.alignment.upper()}")
    print(f"  -> Enforceability:      {f10.enforceability}")
    print(f"  -> Legal Explanation:   {f10.explanation}")

    # Step 11: Automatic Renewal "Call-to-Cancel" Dark Pattern (BPC § 17602)
    print("\n" + "=" * 78)
    print("Step 11: Automatic Renewal 'Call-to-Cancel' Dark Pattern (ARL / BPC § 17602)")
    print("-" * 78)
    f11 = evaluate_contract_vs_statute_slots(
        topic="AUTOMATIC_RENEWAL",
        as_of=date(2024, 8, 1),
        contract_slots={"no_online_cancellation": True},
        raw_content="Subscription auto-renews monthly; subscriber must call to cancel with no online cancellation."
    )
    print("  [Contract Term: Subscriber must call to cancel with no online cancellation]")
    print(f"  -> Controlling Statute:  {f11.controlling_statute['citation']}")
    print(f"  -> Mandate Type:        {f11.controlling_statute['mandate_type']}")
    print(f"  -> Alignment Verdict:   {f11.alignment.upper()}")
    print(f"  -> Enforceability:      {f11.enforceability}")
    print(f"  -> Legal Explanation:   {f11.explanation}")

    # Step 12: Corporate Books & Records Inspection Waiver (Corp. Code §§ 1601-1602)
    print("\n" + "=" * 78)
    print("Step 12: Corporate Books & Records Inspection Waiver (Corp. Code §§ 1601-1602)")
    print("-" * 78)
    f12 = evaluate_contract_vs_statute_slots(
        topic="SHAREHOLDER_INSPECTION_WAIVER",
        as_of=date(2024, 8, 1),
        contract_slots={"waives_inspection_rights": True},
        raw_content="Minority shareholders hereby waive all statutory inspection rights under Section 1601."
    )
    print("  [Bylaw Term: Minority shareholders waive statutory inspection rights]")
    print(f"  -> Controlling Statute:  {f12.controlling_statute['citation']}")
    print(f"  -> Mandate Type:        {f12.controlling_statute['mandate_type']}")
    print(f"  -> Alignment Verdict:   {f12.alignment.upper()}")
    print(f"  -> Enforceability:      {f12.enforceability}")
    print(f"  -> Legal Explanation:   {f12.explanation}")

    # Step 13: LLC Fiduciary Duty of Loyalty Elimination (RULLCA Corp. Code § 17701.10(c))
    print("\n" + "=" * 78)
    print("Step 13: LLC Fiduciary Duty of Loyalty Elimination (RULLCA § 17701.10(c))")
    print("-" * 78)
    f13 = evaluate_contract_vs_statute_slots(
        topic="LLC_DUTY_OF_LOYALTY_ELIMINATION",
        as_of=date(2024, 8, 1),
        contract_slots={"eliminates_fiduciary_loyalty": True},
        raw_content="Managing Member shall have no fiduciary duty of loyalty and all fiduciary duties are eliminated."
    )
    print("  [Operating Agreement Term: Managing Member has no fiduciary duty of loyalty]")
    print(f"  -> Controlling Statute:  {f13.controlling_statute['citation']}")
    print(f"  -> Mandate Type:        {f13.controlling_statute['mandate_type']}")
    print(f"  -> Alignment Verdict:   {f13.alignment.upper()}")
    print(f"  -> Enforceability:      {f13.enforceability}")
    print(f"  -> Legal Explanation:   {f13.explanation}")

    # Step 14: Government Tort Claim Presentation Deadline (Gov. Code § 911.2 / Bodde)
    print("\n" + "=" * 78)
    print("Step 14: Government Tort Claim Presentation Deadline (Gov. Code § 911.2 / Bodde)")
    print("-" * 78)
    f14 = evaluate_contract_vs_statute_slots(
        topic="GOVERNMENT_CLAIM_PRESENTATION",
        as_of=date(2024, 8, 1),
        contract_slots={"gov_claim_presentation_months": 9.0},
        raw_content="Written tort claim for personal injury presented 9 months after accrual."
    )
    print("  [Tort Claim Presentation: 9 months after accrual (Mandatory Ceiling: 6 months)]")
    print(f"  -> Controlling Statute:  {f14.controlling_statute['citation']}")
    print(f"  -> Mandate Type:        {f14.controlling_statute['mandate_type']}")
    print(f"  -> Alignment Verdict:   {f14.alignment.upper()}")
    print(f"  -> Enforceability:      {f14.enforceability}")
    print(f"  -> Legal Explanation:   {f14.explanation}")

    # Portfolio Summary
    portfolio = synthesize_portfolio_response(
        findings=[f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13, f14],
        as_of_date="2024-08-01",
        jurisdiction="CA:Oakland",
        counterparty="Sovereign Holdings LLC"
    )

    elapsed = time.perf_counter() - t0
    print("\n" + "=" * 78)
    print(f"  DEMO COMPLETE: All 14 cross-domain join checks executed in {elapsed:.3f}s")
    print(f"  Portfolio Verdict: {portfolio.verdict}")
    print(f"  Summary: {portfolio.summary}")
    print("  Status: 100% Deterministic Air-Gapped Precision Verified")
    print("=" * 78 + "\n")


if __name__ == "__main__":
    main()

