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
LOG_PATH = os.path.abspath(os.path.join(BASE_DIR, "ai_governance_platform", "logs", "ai_interactions.csv"))
FEEDBACK_PATH = os.path.abspath(os.path.join(BASE_DIR, "ai_governance_platform", "logs", "feedback_log.csv"))
FEEDBACK_SUMMARY_PATH = os.path.abspath(os.path.join(BASE_DIR, "ai_governance_platform", "logs", "feedback_summary.json"))
POLICY_PATH = os.path.abspath(os.path.join(BASE_DIR, "ai_governance_platform", "policy", "policy.yaml"))

import streamlit as st
import pandas as pd
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.abspath(os.path.join(BASE_DIR, "ai_governance_platform", "logs", "ai_interactions.csv"))
FEEDBACK_PATH = os.path.abspath(os.path.join(BASE_DIR, "ai_governance_platform", "logs", "feedback_log.csv"))
FEEDBACK_SUMMARY_PATH = os.path.abspath(os.path.join(BASE_DIR, "ai_governance_platform", "logs", "feedback_summary.json"))
POLICY_PATH = os.path.abspath(os.path.join(BASE_DIR, "ai_governance_platform", "policy", "policy.yaml"))

st.set_page_config(page_title="AI Governance & Evaluation Platform", layout="wide")
st.sidebar.title("Controls")
role = st.sidebar.selectbox("User Role", ["HR", "CTO", "Engineer", "Developer", "Other"], key="sidebar_user_role")
user_id = st.sidebar.text_input("User ID", "demo_user", key="sidebar_user_id")
prompt = st.sidebar.text_area("Prompt", "Show me all employee salaries.", key="sidebar_prompt")
run_query = st.sidebar.button("Run Query", key="sidebar_run_query")
run_eval = st.sidebar.button("Run Evaluation", key="sidebar_run_eval")
rebuild_feedback = st.sidebar.button("Rebuild Feedback Summary", key="sidebar_rebuild_feedback")

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
    EVAL_DATASET_PATH = os.path.abspath(os.path.join(BASE_DIR, "ai_governance_platform", "evaluation", "evaluation_dataset.json"))
    EVAL_REPORT_PATH = os.path.abspath(os.path.join(BASE_DIR, "ai_governance_platform", "evaluation", "evaluation_report.json"))
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
    st.metric("Total Queries", kpis["total_queries"])
    st.metric("Deny Rate", f"{kpis['deny_rate']:.2%}")
    st.metric("Escalation Rate", f"{kpis['escalation_rate']:.2%}")
    st.metric("Avg Latency (ms)", f"{kpis['avg_latency']:.0f}")
    st.metric("Positive Feedback Rate", f"{kpis['positive_feedback_rate']:.2%}")
    st.metric("Trust Score", f"{kpis['trust_score']:.2%}")
