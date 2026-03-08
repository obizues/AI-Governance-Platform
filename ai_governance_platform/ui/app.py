import os
import json
import sys
from ai_governance_platform.audit_logging.audit_logger import AuditLogger
from ai_governance_platform.feedback.feedback_logger import FeedbackLogger
from ai_governance_platform.feedback.summary import FeedbackSummary
from ai_governance_platform.metrics.kpis import compute_kpis
from ai_governance_platform.policy.policy_engine import PolicyEngine
from ai_governance_platform.policy.feedback_gate import FeedbackGate
from ai_governance_platform.providers.provider_interface import StubProvider
from ai_governance_platform.evaluation.evaluation_runner import EvaluationRunner

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "logs", "ai_interactions.csv"))
FEEDBACK_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "logs", "feedback_log.csv"))
FEEDBACK_SUMMARY_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "logs", "feedback_summary.json"))
POLICY_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "policy", "policy.yaml"))

import streamlit as st
import pandas as pd
import hashlib
st.sidebar.markdown("""
<div style='background:#eaf6ff;border:1.5px solid #b3e5fc;padding:10px 12px 8px 12px;margin-bottom:12px;text-align:center;border-radius:8px;'>
    <span style='font-size:1.08em;font-weight:600;color:#1976d2;'>App version:</span><br>
    <span style='font-size:1.05em;color:#222;'>v0.3.0 - Modular AI Governance, Audit Logging, Policy Engine, Feedback, Streamlit UI</span>
</div>
<div class='sidebar-card' style='background:#eaf6ff;font-size:0.93em;margin-bottom:16px;border:1.5px solid #b3e5fc;padding:8px 8px 6px 8px;'>
    <div style='font-weight:700;font-size:1em;line-height:1.2;margin-bottom:2px;text-align:center;'>
        <span style="font-size:1.05em;vertical-align:middle;">🤖</span> AI Governance & Evaluation Platform
    </div>
    <div style='margin:0 0 0 0;font-size:0.91em;line-height:1.35;text-align:center;'>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">📝</span> <span>Audit Logging for all AI interactions</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">⚖️</span> <span>Policy Engine for query risk assessment</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">💬</span> <span>Feedback logging and summary</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">📊</span> <span>System Health KPIs and metrics</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">🖥️</span> <span>Streamlit-based modern UI</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">🌐</span> <span>Open-source, modular Python codebase</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar.expander("ℹ️ About This Project", expanded=False):
    st.markdown("""
Modular AI Governance & Evaluation Platform
- Audit logging for all AI interactions
- Policy engine for risk assessment and controls
- Feedback logging and summary for continuous improvement
- System Health KPIs for operational visibility
- Streamlit-based modern UI for business users
- Open-source, extensible Python codebase
- Designed for CTOs, CEOs, hiring managers, and PE operators

**Target Audience:**
Executives, engineering leaders, HR, private equity operators, and technical decision-makers seeking robust AI governance, auditability, and evaluation for enterprise AI systems.

**Key Features:**
- Modular audit logging and feedback
- Policy-driven query evaluation
- System health metrics and KPIs
- Streamlit UI for easy access and reporting
- Open-source, extensible design
""", unsafe_allow_html=True)
with st.sidebar.expander("&#128193; Project Documentation", expanded=False):
    st.markdown("**Project Documentation**")
    st.markdown("<span style='font-size:1.05em;'>🌐</span> [GitHub Repository](https://github.com/obizues/AI-Governance-Platform)", unsafe_allow_html=True)
    st.markdown("<span style='font-size:1.05em;'>📄</span> **Documentation**", unsafe_allow_html=True)
    st.markdown("- <span style='font-size:1.05em;'>📘</span> [README.md](https://github.com/obizues/AI-Governance-Platform/blob/main/README.md): Platform overview, setup, features", unsafe_allow_html=True)
    st.markdown("- <span style='font-size:1.05em;'>📝</span> [CHANGELOG.md](https://github.com/obizues/AI-Governance-Platform/blob/main/CHANGELOG.md): Release notes and updates", unsafe_allow_html=True)
    st.markdown("- <span style='font-size:1.05em;'>🗂️</span> [System Architecture](https://github.com/obizues/AI-Governance-Platform/blob/main/docs/architecture.md): Design and flow diagrams", unsafe_allow_html=True)
    st.markdown("**Key Sections:**\n- Audit Logging\n- Policy Engine\n- Feedback & Evaluation\n- System Health KPIs\n- Deployment & Usage Guide")
with st.sidebar.expander("&#128295; Tech Stack", expanded=False):
    st.markdown("""
<span style='font-size:1em;'>
<ul style='margin-bottom:0; padding-left: 18px;'>
<li>Python 3.10+</li>
<li>Streamlit (UI)</li>
<li>pandas (data handling)</li>
<li>Audit logging (CSV, JSON)</li>
<li>Policy engine (YAML-based rules)</li>
<li>Feedback logging & summary</li>
<li>System Health KPIs</li>
<li>pytest (testing, audit validation)</li>
<li>GitHub Actions (CI/CD)</li>
</ul>
</span>
""", unsafe_allow_html=True)
with st.sidebar.expander("🧩 System Design Notes", expanded=False):
    st.markdown("""
<span style='font-size:1em;'>
<ul style='margin-bottom:0; padding-left: 18px;'>
<li><b>Modular Architecture:</b> Separate modules for audit logging, policy engine, feedback, metrics, and UI.</li>
<li><b>Audit Logging:</b> All AI interactions are logged for traceability and compliance.</li>
<li><b>Policy Engine:</b> YAML-based rules for query risk assessment and control enforcement.</li>
<li><b>Feedback Logging:</b> User feedback is logged and summarized for continuous improvement.</li>
<li><b>System Health KPIs:</b> Real-time metrics for queries, deny rate, escalation, latency, trust score, and feedback.</li>
<li><b>Streamlit UI:</b> Modern, business-focused interface with tabs for queries, feedback, and health.</li>
<li><b>Open Source:</b> Extensible Python codebase, GitHub-hosted, CI/CD enabled.</li>
<li><b>Deployment:</b> Streamlit Cloud, local, or containerized environments.</li>
<li><b>Security & Privacy:</b> All processing is local; no data leaves the user's environment.</li>
</ul>
</span>
""", unsafe_allow_html=True)
    
# --- Top blue app title bar (centered, above personal info) ---
st.markdown(
    """
    <style>
        .main-title-banner {
            background: #1976d2;
            color: #fff;
            font-size: 1.45em;
            font-weight: 700;
            text-align: center;
            margin: 0 auto 0 auto;
            padding: 0.7em 0 0.7em 0;
            box-sizing: border-box;
            border-radius: 0 0 18px 18px;
            box-shadow: 0 2px 8px rgba(25, 118, 210, 0.10);
            letter-spacing: 0.01em;
            max-width: 700px;
        }
        .main-title-banner .emoji {
            font-size: 1.3em;
            vertical-align: middle;
            margin-right: 0.18em;
            filter: none;
        }
    </style>
    <div class="main-title-banner">
        <span class="emoji">🤖</span> AI Governance & Evaluation Platform
    </div>
    """, unsafe_allow_html=True)

# --- Personal Information Banner ---
personal_info_banner = """
<style>
.app-title-banner {
    background: #f5f5f5;
    color: #222;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 1.08em;
    font-weight: 500;
    text-align: center;
    margin: 0.5em auto 0 auto;
    padding: 0.5em 0 0.5em 0;
    box-sizing: border-box;
    border-radius: 0 0 12px 12px;
    box-shadow: 0 2px 8px rgba(25, 118, 210, 0.08);
    max-width: 700px;
}
.app-title-banner .name-title {
    font-size: 1.18em;
    font-weight: 700;
    color: #1976d2;
    margin-bottom: 0.1em;
}
.app-title-banner .subtitle {
    font-size: 0.98em;
    color: #1976d2;
    margin-bottom: 0.2em;
}
.app-title-banner .links, .app-title-banner .project-links {
    font-size: 0.97em;
    margin-bottom: 0.1em;
}
.app-title-banner a {
    color: #1976d2;
    text-decoration: underline;
    margin: 0 8px;
    font-size: 0.97em;
}
.app-title-banner .project-links {
    margin-top: 0.1em;
}
    @media (max-width: 600px) {
        .app-title-banner { font-size: 0.93em; }
        .app-title-banner .name-title { font-size: 1em; }
        .app-title-banner .subtitle { font-size: 0.91em; }
        .app-title-banner .links, .app-title-banner .project-links { font-size: 0.91em; }
    }
</style>
<div class="app-title-banner">
    <div class="name-title" style="font-size:0.95em; font-weight:400; margin-bottom:0.08em; text-align:center; color:#1976d2;"><b>Chris Obermeier</b> | SVP of Engineering</div>
    <div class="subtitle" style="background:transparent;border-radius:0;padding:2px 8px;font-size:0.83em;text-align:center;margin-bottom:0.08em;color:#64b5f6;font-weight:400;">Enterprise Platform & AI Transformation | Led 100+ Engineer Orgs | PE & Revenue-Scale Modernization</div>
    <div class="links" style="font-size:0.92em; font-weight:400; margin-bottom:0em; text-align:center;">
        <a href="https://www.linkedin.com/in/chris-obermeier/" target="_blank">LinkedIn</a> |
        <a href="https://github.com/obizues" target="_blank">GitHub</a> |
        <a href="mailto:chris.obermeier@gmail.com" target="_blank">Email</a>
    </div>
    <div class="project-links" style="font-size:0.92em; font-weight:400; margin-top:0em; text-align:center;">
        <span style="margin-right:4px;">&#11088;</span><a href="https://github.com/obizues/AI-Governance-Platform" target="_blank">Star on GitHub</a> |
        <span style="margin-right:4px;">&#128214;</span><a href="https://github.com/obizues/AI-Governance-Platform/blob/main/README.md" target="_blank">Read Documentation</a>
    </div>
</div>
"""
st.markdown(personal_info_banner, unsafe_allow_html=True)

st.set_page_config(page_title="AI Governance & Evaluation Platform", layout="wide")

provider = StubProvider()
policy_engine = PolicyEngine(POLICY_PATH)
audit_logger = AuditLogger(LOG_PATH)
feedback_logger = FeedbackLogger(FEEDBACK_PATH)
feedback_gate = FeedbackGate(FEEDBACK_SUMMARY_PATH)

role = st.selectbox("User Role", ["HR", "CTO", "Engineer", "Developer", "Other"], key="main_user_role")
user_id = st.text_input("User ID", "demo_user", key="main_user_id")
prompt = st.text_area("Prompt", "Show me all employee salaries.", key="main_prompt")
run_query = st.button("Run Query", key="main_run_query")
run_eval = st.button("Run Evaluation", key="main_run_eval")
rebuild_feedback = st.button("Rebuild Feedback Summary", key="main_rebuild_feedback")



provider = StubProvider()
policy_engine = PolicyEngine(POLICY_PATH)
audit_logger = AuditLogger(LOG_PATH)
feedback_logger = FeedbackLogger(FEEDBACK_PATH)
feedback_gate = FeedbackGate(FEEDBACK_SUMMARY_PATH)
tabs = st.tabs(["Live Query", "Feedback Log", "System Health"])

with tabs[0]:
    st.header("Live Query")
    # Always show info message if no query context is present
    if st.session_state.get("show_feedback_info", False):
        st.info("Feedback submitted successfully! Enter a prompt and click 'Run Query' to get started.")
        st.session_state["show_feedback_info"] = False
    elif "last_query_context" not in st.session_state and not run_query:
        st.info("No query has been run yet. Enter a prompt and click 'Run Query' to get started.")
    # Store last query context in session state
    if run_query:
        import time
        start_time = time.time()
        context = {
            "user_id": user_id,
            "user_role": role,
            "prompt": prompt,
            "confidence_score": 0.95,
            "retrieved_sources_present": True
        }
        context["prompt_hash"] = hashlib.sha256(prompt.encode()).hexdigest()
        decision = feedback_gate.apply_feedback_gate(context, policy_engine)
        response = provider.generate_response(prompt)
        end_time = time.time()
        response_time_ms = int((end_time - start_time) * 1000)
        st.session_state["last_query_context"] = context
        st.session_state["last_query_response"] = response
        st.session_state["last_query_decision"] = decision
        # Log query to ai_interactions.csv
        audit_entry = {
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": user_id,
            "user_role": role,
            "prompt": prompt,
            "response": response,
            "response_time_ms": response_time_ms,
            "confidence_score": context["confidence_score"],
            "risk_level": decision.get("risk_level", ""),
            "decision": decision.get("decision", ""),
            "rule_triggered": decision.get("rule_triggered", ""),
            "reason": decision.get("reason", ""),
            "required_controls": decision.get("required_controls", "")
        }
        audit_logger.log_interaction(audit_entry)
    # Show last query result if available
    if "last_query_context" in st.session_state:
        context = st.session_state["last_query_context"]
        response = st.session_state["last_query_response"]
        decision = st.session_state["last_query_decision"]
        st.write(f"**Query:** {context['prompt']}")
        st.write(f"**Decision:** {decision['decision']}")
        st.write(f"**Risk Level:** {decision['risk_level']}")
        st.write(f"**Rule Triggered:** {decision.get('rule_triggered') or 'No rule triggered'}")
        st.write(f"**Reason:** {decision.get('reason') or 'No reason'}")
        st.write(f"**Response:** {response if response else '[No response generated]'}")
        thumbs = st.radio("Rate the system's response:", ["👍", "👎"], key="feedback_radio")
        submit = st.button("Submit Feedback")
        cleanup = st.button("Cleanup Downvotes for This Prompt")
        if submit:
            st.session_state["show_feedback_info"] = True
            feedback_entry = [
                pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                context["user_role"],
                context["prompt"],
                response,
                thumbs if thumbs in ["👍", "👎"] else ""
            ]
            try:
                import csv
                import os
                # Write header if file is empty
                if not os.path.exists(FEEDBACK_PATH) or os.stat(FEEDBACK_PATH).st_size == 0:
                    with open(FEEDBACK_PATH, mode="w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(["timestamp", "user_role", "prompt", "response", "feedback"])
                with open(FEEDBACK_PATH, mode="a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(feedback_entry)
                    f.flush()
                summary = FeedbackSummary(FEEDBACK_PATH, FEEDBACK_SUMMARY_PATH)
                summary.rebuild_summary()
                st.session_state["show_feedback_banner"] = True
                # Clear last query context and rerun to reset screen
                del st.session_state["last_query_context"]
                del st.session_state["last_query_response"]
                del st.session_state["last_query_decision"]
                st.rerun()
            except Exception as e:
                st.warning(f"Feedback logging failed: {e}")
        if cleanup:
            import csv
            import os
            prompt_text = context["prompt"]
            # Remove all 👎 feedback for this prompt
            if os.path.exists(FEEDBACK_PATH):
                with open(FEEDBACK_PATH, mode="r", encoding="utf-8") as f:
                    rows = list(csv.reader(f))
                header = rows[0]
                filtered = [row for row in rows[1:] if not (row[2] == prompt_text and row[4] == "👎")]
                with open(FEEDBACK_PATH, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(header)
                    writer.writerows(filtered)
            # Rebuild feedback summary
            summary = FeedbackSummary(FEEDBACK_PATH, FEEDBACK_SUMMARY_PATH)
            summary.rebuild_summary()
            st.success("Downvotes for this prompt have been cleaned up!")




if run_eval:
    st.info("Running evaluation...")
    EVAL_DATASET_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "evaluation", "evaluation_dataset.json"))
    EVAL_REPORT_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "evaluation", "evaluation_report.json"))
    runner = EvaluationRunner(EVAL_DATASET_PATH, EVAL_REPORT_PATH)
    runner.run(provider, policy_engine)
    st.success(f"Evaluation report generated at {EVAL_REPORT_PATH}")

if rebuild_feedback:
    st.info("Rebuilding feedback summary...")
    summary = FeedbackSummary(FEEDBACK_PATH, FEEDBACK_SUMMARY_PATH)
    summary.rebuild_summary()
    st.success("Feedback summary rebuilt!")
    st.rerun()

with tabs[1]:
    st.header("Feedback Log")
    if os.path.exists(FEEDBACK_PATH):
        try:
            df = pd.read_csv(FEEDBACK_PATH)
            if df.empty:
                st.info("No feedback entries found.")
            else:
                role_filter = st.selectbox("Role Filter", ["All"] + sorted(df["user_role"].unique()), key="feedback_role_filter")
                feedback_filter = st.selectbox("Feedback Filter", ["All", "👍", "👎"], key="feedback_type_filter")
                n_rows = st.slider("Show Last N Rows", 10, 100, 20, key="feedback_n_rows_slider")
                filtered = df.copy()
                if role_filter != "All":
                    filtered = filtered[filtered["user_role"] == role_filter]
                if feedback_filter != "All":
                    filtered = filtered[filtered["feedback"] == feedback_filter]
                st.dataframe(filtered.tail(n_rows))
        except pd.errors.EmptyDataError:
            st.info("No feedback log found or file is empty.")
    else:
        st.info("No feedback log found.")

with tabs[2]:
    st.header("System Health KPIs")
    kpis = compute_kpis(LOG_PATH, FEEDBACK_PATH)
    st.subheader("Operational KPIs")
    st.metric("Total Queries", kpis["total_queries"])
    st.metric("Deny Rate", f"{kpis['deny_rate']:.2%}")
    st.metric("Escalation Rate", f"{kpis['escalation_rate']:.2%}")
    st.metric("Avg Latency (ms)", f"{kpis['avg_latency']:.0f}")
    st.metric("Positive Feedback Rate", f"{kpis['positive_feedback_rate']:.2%}")
    st.metric("Trust Score", f"{kpis['trust_score']:.2%}")
    st.subheader("Evaluation KPIs")
    if kpis.get("eval_pass_rate") is not None:
        st.metric("Evaluation Pass Rate", f"{kpis['eval_pass_rate']:.2%}")
    if kpis.get("eval_avg_score") is not None:
        st.metric("Evaluation Avg Score", f"{kpis['eval_avg_score']:.2%}")

