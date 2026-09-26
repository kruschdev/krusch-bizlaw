"""
src/frontend/app.py
===================
Streamlit Web UI for KruschBizLaw.
Default loopback binding: http://127.0.0.1:8507
Aesthetics: Cyber-Executive Slate/Navy & Gold, High-Contrast Typography, WCAG AAA.
"""

from __future__ import annotations

from datetime import date
import streamlit as st

st.set_page_config(
    page_title="KruschBizLaw | Sovereign Statutory Compliance Platform",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Contrast CSS
st.markdown("""
<style>
    /* Dark glassmorphism & typography */
    .stApp {
        background-color: #07090E;
        color: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* High-contrast React-Aria navigation tabs */
    div[data-testid="stTab"] p,
    div[data-testid="stTab"] span,
    div[data-testid="stTab"] div,
    button[data-baseweb="tab"] p,
    button[data-baseweb="tab"] span {
        color: #F8FAFC !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }

    button[aria-selected="true"] p,
    button[aria-selected="true"] span {
        color: #FBBF24 !important;
        font-weight: 700 !important;
    }

    /* Cards */
    .compliance-card-void {
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .compliance-card-enforceable {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .compliance-card-gap {
        background: rgba(245, 158, 11, 0.08);
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Imports from engine
from src.engine.join import evaluate_contract_vs_statute_slots, synthesize_portfolio_response
from src.engine.mandates import STATUTORY_MANDATES
from src.backend.clients import KruschBizClient, KruschLawClient

biz_client = KruschBizClient()
law_client = KruschLawClient()

# Header
st.title("⚖️ KruschBizLaw")
st.caption("**Sovereign Cross-Domain Statutory Compliance Engine & Contract-vs-Statute Join Platform** • *v0.1.0-alpha.1*")

# Sidebar
with st.sidebar:
    st.subheader("🖥️ Fleet Substrate Status")
    biz_up = biz_client.check_health()
    law_up = law_client.check_health()

    st.markdown(f"""
    - **KruschBiz (8086)**: {"🟢 Online" if biz_up else "🔴 Offline (Mock Active)"}
    - **KruschLaw (8085)**: {"🟢 Online" if law_up else "🔴 Offline (Mock Active)"}
    - **KruschBizLaw (8087)**: 🟢 Core In-Process
    """)
    st.divider()
    st.markdown("""
    **Core Architecture**:
    - **KruschLaw**: Statutory precedence DAG & California tenant authorities.
    - **KruschBiz**: Commercial contract graph & controlling precedence.
    - **KruschBizLaw**: Unifies both via deterministic slot cross-examinations.
    """)

tab1, tab2, tab3 = st.tabs([
    "🔍 Compliance Audit (\"The Join\")",
    "📊 Empirical Benchmark Suite (11/11)",
    "📜 Statutory Mandates Registry"
])

# TAB 1: The Join
with tab1:
    st.markdown("### 🔍 Execute Statutory Compliance Cross-Examination")
    st.write("Compare controlling commercial contract clauses resolved via KruschBiz against non-waivable statutory floors and ceilings resolved via KruschLaw.")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        counterparty = st.text_input("Counterparty / Tenant Entity", value="Highland Residential LLC")
        property_type = st.selectbox("Property Type", ["residential", "commercial"], index=0)
    with col2:
        jurisdiction = st.selectbox("Jurisdiction", ["CA:Oakland", "CA:San Francisco", "CA:Los Angeles", "California"], index=0)
        as_of_date_val = st.date_input("Evaluation Date (as_of_date)", value=date(2024, 8, 1))
    with col3:
        selected_topics = st.multiselect(
            "Statutory Doctrines to Audit",
            list(STATUTORY_MANDATES.keys()),
            default=["SECURITY_DEPOSIT", "ENTRY_NOTICE", "DEPOSIT_RETURN", "HABITABILITY_WAIVER", "LATE_FEE"]
        )

    st.subheader("📝 Contract Provision Input (Direct Slots or Text)")
    use_manual_input = st.toggle("Inject Custom Contract Slots", value=True)

    contract_slots = {}
    if use_manual_input:
        c_col1, c_col2, c_col3 = st.columns(3)
        with c_col1:
            deposit_months = st.number_input("Deposit (Months Rent)", value=2.0, step=0.5)
            contract_slots["deposit_cap_months"] = deposit_months
        with c_col2:
            entry_hours = st.number_input("Landlord Entry Notice (Hours)", value=12.0, step=6.0)
            contract_slots["entry_notice_hours"] = entry_hours
        with c_col3:
            return_days = st.number_input("Deposit Return Timeline (Days)", value=45.0, step=1.0)
            contract_slots["deposit_return_days"] = return_days

        w_col1, w_col2 = st.columns(2)
        with w_col1:
            waives_hab = st.checkbox("Includes As-Is Habitability Waiver", value=True)
            contract_slots["waives_habitability"] = waives_hab
        with w_col2:
            late_fee = st.number_input("Late Fee Penalty (%)", value=15.0, step=1.0)
            contract_slots["late_penalty_pct"] = late_fee

    if st.button("🚀 Run Compliance Cross-Examination", type="primary"):
        findings = []
        for topic in selected_topics:
            f = evaluate_contract_vs_statute_slots(
                topic=topic,
                as_of=as_of_date_val,
                contract_slots=contract_slots,
                property_type=property_type
            )
            findings.append(f)

        resp = synthesize_portfolio_response(
            findings=findings,
            as_of_date=str(as_of_date_val),
            jurisdiction=jurisdiction,
            counterparty=counterparty
        )

        st.divider()
        st.subheader("📋 Executive Audit Verdict")

        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Overall Verdict", resp.verdict)
        m_col2.metric("Violations / Void Terms", resp.summary["non_compliant"], delta_color="inverse")
        m_col3.metric("Compliant Terms", resp.summary["compliant"])
        m_col4.metric("Coverage Gaps", resp.summary["coverage_gaps"])

        st.markdown("#### ⚖️ Finding Details")
        for finding in resp.findings:
            if finding.enforceability == "VOID_AS_AGAINST_PUBLIC_POLICY":
                card_class = "compliance-card-void"
                badge = "🔴 VOID AS AGAINST PUBLIC POLICY"
            elif finding.alignment == "coverage_gap":
                card_class = "compliance-card-gap"
                badge = "🟡 COVERAGE GAP"
            else:
                card_class = "compliance-card-enforceable"
                badge = "🟢 ENFORCEABLE / COMPLIANT"

            stat_cite = finding.controlling_statute.get("citation", "Statute") if finding.controlling_statute else "No Statute"
            st.markdown(f"""
            <div class="{card_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="font-size: 1.1rem;">{finding.topic}</strong>
                    <span style="font-weight: 700;">{badge}</span>
                </div>
                <p style="margin: 8px 0; color: #E2E8F0;">{finding.explanation}</p>
                <div style="font-size: 0.85rem; color: #94A3B8;">
                    <strong>Controlling Authority:</strong> {stat_cite} &nbsp;|&nbsp; <strong>Trace ID:</strong> <code>{finding.trace_id}</code>
                </div>
            </div>
            """, unsafe_allow_html=True)


# TAB 2: Benchmark
with tab2:
    st.markdown("### 📊 Empirical Benchmark Suite: 11 Fixture Scenarios")
    st.write("Live evaluation harness testing deterministic slot cross-examinations across California statutory milestones.")

    from scripts.eval_benchmark import BENCHMARK_SCENARIOS

    if st.button("▶️ Run Automated Benchmark", type="primary"):
        from scripts.eval_benchmark import run_benchmark
        results = run_benchmark()
        st.success(f"Benchmark Complete! {results['passed']}/{results['total_scenarios']} passed in {results['total_latency_ms']:.2f}ms.")

    st.table([
        {
            "ID": tc["id"],
            "Scenario": tc["name"],
            "Topic": tc["topic"],
            "Date": str(tc["as_of_date"]),
            "Expected Verdict": tc["expected_enforceability"],
            "Controlling Statute": tc["governing_statute"] or "None"
        }
        for tc in BENCHMARK_SCENARIOS
    ])


# TAB 3: Mandates
with tab3:
    st.markdown("### 📜 Statutory Mandates & Non-Waivable Public Policy Registry")
    st.write("Authoritative rules catalog used by KruschBizLaw to evaluate contract slot validity.")

    for topic, data in STATUTORY_MANDATES.items():
        with st.expander(f"📌 {topic} — {data['citation']}"):
            st.write(f"**Mandate Type:** `{data['mandate_type']}`")
            st.write(f"**Non-Waivable Public Policy:** {'Yes (Civil Code)' if data.get('non_waivable') else 'No (Permissive Freedom of Contract)'}")
            st.write(f"**Statutory Text:** {data['statutory_text']}")
