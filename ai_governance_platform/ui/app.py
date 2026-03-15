import csv  # noqa: F401 (kept for any residual usage)
import datetime  # noqa: F401
import io
import json
import os
import sys
import uuid  # noqa: F401
import zipfile  # noqa: F401

import pandas as pd
import streamlit as st

from ai_governance_platform.services.escalation_service import EscalationService
from ai_governance_platform.services.evaluation_service import EvaluationService
from ai_governance_platform.services.extraction_orchestration_service import ExtractionOrchestrationService
from ai_governance_platform.services.feedback_service import FeedbackService
from ai_governance_platform.services.model_monitoring_service import ModelMonitoringService

_scripts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
if _scripts_path not in sys.path:
    sys.path.insert(0, _scripts_path)
from demo_retrain_with_feedback import retrain_with_feedback, reset_active_model_to_baseline


APP_VERSION = "v0.11.3"
BASELINE_MODEL_VERSION = "v0.11.1"

MANIFEST_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "ai_governance_platform", "logs", "retrain_manifest.json")
)

# Thin wrappers kept so existing call-sites inside main() work with no change.
def _extract_report_metric(report_text, label, metric_name):
    return ModelMonitoringService.extract_report_metric(report_text, label, metric_name)

def _parse_semver(version):
    return ModelMonitoringService.parse_semver(version)

def _is_older_version(version, reference):
    return ModelMonitoringService.is_older_version(version, reference)

def _load_active_model_metadata():
    return ModelMonitoringService.load_active_model_metadata(MANIFEST_PATH)
        
REVIEWER_NAMES = ["Alice Smith", "Bob Johnson", "Chris Obermeier", "Dana Lee", "Evan Kim"]


def _init_session_state():
    st.session_state.setdefault("reviewed_escalations", set())
    st.session_state.setdefault("current_escalation_idx", 0)
    st.session_state.setdefault("submitted_human_feedback", set())

def main():
    _init_session_state()  # MUST be first in main()
    # ...existing code...
    import streamlit as st
    import pandas as pd
    # Title banner
    st.markdown("""
<style>
    .main-title-banner {
        background: #1976d2;
        color: #fff;
        font-family: 'Segoe UI', 'Arial', sans-serif;
        font-size: 1.35em;
        font-weight: 600;
        text-align: center;
        margin: 0 auto 0 auto;
        padding: 0.7em 0 0.7em 0;
        box-sizing: border-box;
        border-radius: 0 0 18px 18px;
        box-shadow: 0 2px 8px rgba(25, 118, 210, 0.10);
        margin-right: 0.18em;
        filter: none;
    }
    .emoji {
        font-size: 1.3em;
        margin-right: 0.18em;
    }
    .app-title-banner {
        background: #eaf6ff;
        color: #fff;
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
<div class="main-title-banner">
    <span class="emoji">🤖</span> AI Governance & Evaluation Platform
</div>
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
""", unsafe_allow_html=True)

    # Sidebar with app version and dropdowns
    st.sidebar.markdown(f"""
<div style='background:#eaf6ff;border:1.5px solid #b3e5fc;padding:10px 12px 8px 12px;margin-bottom:12px;text-align:center;border-radius:8px;'>
<span style='font-size:1.08em;font-weight:600;color:#1976d2;'>App version:</span><br>
{APP_VERSION} - HIL governance, training labels, retraining, KPI monitoring, and model version control
</div>
""", unsafe_allow_html=True)
    st.sidebar.markdown(f"""
<div class='sidebar-card' style='background:#eaf6ff;font-size:0.93em;margin-bottom:16px;border:1.5px solid #b3e5fc;padding:8px 8px 6px 8px;'>
<div style='font-weight:700;font-size:1em;line-height:1.2;margin-bottom:2px;text-align:center;'>
<span style="font-size:1.05em;vertical-align:middle;">&#129302;</span> AI Governance & Evaluation Platform {APP_VERSION}
</div>
<div style='margin:0 0 0 0;font-size:0.91em;line-height:1.35;text-align:center;'>
<span style="font-size:1em;">&#128221;</span> <span>Audit logging and governance history</span>
</div>
<div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
<span style="font-size:1em;">&#9878;</span> <span>Policy-driven review controls and escalation workflow</span>
</div>
<div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
<span style="font-size:1em;">&#128172;</span> <span>Human training labels and governed retraining</span>
</div>
<div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
<span style="font-size:1em;">&#128721;</span> <span>Escalation decisions for low-confidence document fields</span>
</div>
<div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
<span style="font-size:1em;">&#128200;</span> <span>KPI monitoring for invalid recall, macro F1, and throughput</span>
</div>
<div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
<span style="font-size:1em;">&#128196;</span> <span>Document extraction, validation, and confidence scoring</span>
</div>
<div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
<span style="font-size:1em;">&#128451;</span> <span>Model versioning, audit review, and baseline reset</span>
</div>
<div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
<span style="font-size:1em;">&#128421;</span> <span>Streamlit-based modern UI</span>
</div>
<div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
<span style="font-size:1em;">&#127760;</span> <span>Open-source, modular Python codebase</span>
</div>
</div>
""", unsafe_allow_html=True)
    # Restore Demo Files expander at the bottom of the sidebar
    import glob
    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    demo_dir = os.path.join(BASE_DIR, '..', '..', 'sample_zips')
    demo_files = sorted([os.path.basename(f) for f in glob.glob(os.path.join(demo_dir, '*')) if os.path.isfile(f)])
    with st.sidebar.expander("🗃️ Demo Files", expanded=False):
        for fname in demo_files:
            fpath = os.path.join(demo_dir, fname)
            with open(fpath, "rb") as f:
                st.download_button(
                    label=f"Download {fname}",
                    data=f.read(),
                    file_name=fname,
                    mime="application/octet-stream"
                )
        st.markdown("<span style='font-size:0.95em;color:#888;'>Click to download demo files for testing.</span>", unsafe_allow_html=True)

    with st.sidebar.expander("ℹ️ About This Project", expanded=False):
        st.markdown("""
    This platform showcases an end-to-end AI governance workflow for document extraction and validation. It combines confidence-based escalation, human review, governed training-label capture, model retraining, versioned deployment, and KPI monitoring in one auditable experience.

    **Target Audience:**
    Executives, engineering leaders, technical evaluators, and operators who need a practical demonstration of safe, observable, and improvable enterprise AI workflows.

    **Key Features:**
    - Audit logging and governance history
    - Policy-driven escalation and reviewer controls
    - Human training labels with source-document verification
    - Governed retraining with active model version control
    - KPI monitoring for invalid recall, macro F1, pending labels, and workflow throughput
    - Document extraction, validation, and confidence scoring
    - Baseline reset for replayable before/after demos
    - Streamlit-based multi-tab operator experience
    - Modular Python services and inspectable logs for demo transparency
    """, unsafe_allow_html=True)

    with st.sidebar.expander("&#128193; Project Documentation", expanded=False):
        st.markdown("**Project Documentation**")
        st.markdown("<span style='font-size:1.05em;'>🌐</span> [GitHub Repository](https://github.com/obizues/AI-Governance-Platform)", unsafe_allow_html=True)
        st.markdown("- <span style='font-size:1.05em;'>📘</span> [README.md](https://github.com/obizues/AI-Governance-Platform/blob/main/README.md): Project overview, setup, features", unsafe_allow_html=True)
        st.markdown("- <span style='font-size:1.05em;'>📝</span> [CHANGELOG.md](https://github.com/obizues/AI-Governance-Platform/blob/main/CHANGELOG.md): Release notes and updates", unsafe_allow_html=True)
        st.markdown("- <span style='font-size:1.05em;'>🗂️</span> [System Architecture](https://github.com/obizues/AI-Governance-Platform/blob/main/docs/architecture.md): Design and flow diagrams", unsafe_allow_html=True)
        st.markdown("**Key Sections:**\n- HIL workflow and escalation flow\n- Training-label and retraining architecture\n- KPI and governance monitoring\n- Baseline reset and model versioning\n- Deployment and usage guide")

    with st.sidebar.expander("&#128295; Tech Stack", expanded=False):
        st.markdown("""
<span style='font-size:1em;'>
<ul style='margin-bottom:0; padding-left: 18px;'>
<li>Python 3.10+ application runtime</li>
<li>Streamlit for the multi-tab governance UI</li>
<li>pandas and JSON/CSV log persistence for audit and feedback data</li>
<li>pdfplumber for PDF field extraction</li>
<li>scikit-learn RandomForest + joblib for field-validation models and versioned artifacts</li>
<li>matplotlib, Altair, and Plotly for KPI monitoring and trend visualization</li>
<li>YAML policy configuration for review and escalation controls</li>
<li>Modular Python service layer for extraction, escalation, feedback, and evaluation</li>
<li>Pytest for service-level regression coverage</li>
</ul>
""", unsafe_allow_html=True)

    with st.sidebar.expander("📝 System Design Notes", expanded=False):
        st.markdown("""
**Key architectural decisions**
<li><b>The Streamlit UI is orchestration only;</b> extraction, escalation, feedback, and evaluation logic live in dedicated services.</li>
<li><b>Operational escalation review is separate from model-training feedback;</b> governance decisions are logged without polluting training labels.</li>
<li><b>Only human-verified ground-truth labels are eligible for retraining;</b> 'cannot_verify' stays out of the training export.</li>
<li><b>The deployed model is always the active artifact</b> at <code>field_validation_rf_encoded_model.joblib</code>, while timestamped backups preserve version history.</li>
<li><b>Retraining is manifest-driven and auditable;</b> each run records model version, metrics, label counts, and outcome history.</li>
<li><b>KPI monitoring prioritizes governance-relevant quality signals</b> such as invalid recall, macro F1, review throughput, and pending label volume.</li>
<li><b>Baseline reset is built in</b> so before/after HIL demo flows can be replayed reliably.</li>
<li><b>Configuration, datasets, model artifacts, and logs are kept in dedicated folders</b> to make the workflow inspectable and demo-friendly.</li>
<li><b>Deployment target:</b> local Streamlit, Streamlit Cloud, or containerized environments.</li>
""", unsafe_allow_html=True)
    # ...existing code...
    # ── Active model version in sidebar ───────────────────────────────────
    _active_model = _load_active_model_metadata()
    _active_model_version = _active_model["version"]
    _active_model_label = _active_model["label"]
    _active_model_color = _active_model["color"]
    _active_model_border = _active_model["border"]
    _active_model_text = _active_model["text"]
    st.sidebar.markdown(
        f"<div style='background:{_active_model_color};border:1px solid {_active_model_border};"
        f"border-radius:8px;padding:8px 12px;margin-bottom:12px;'>"
        f"<b style='color:{_active_model_text};'>Active Model</b><br>"
        f"<span style='font-size:0.82em;color:{_active_model_text};word-break:break-all;'>{_active_model_label}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    tabs = st.tabs(["Extract & Validate", "Escalation Decisions", "Human Training Labels", "Model Monitoring", "Governance & Audit"])
    with tabs[0]:
        st.markdown("""
<div style='background:#eaf6ff;padding:8px 0 8px 0;text-align:center;font-size:1.08em;font-weight:500;border-radius:8px;margin-bottom:8px;'>
<b>Step 1: Extract Documents & Score Confidence</b>
</div>
""", unsafe_allow_html=True)
        st.markdown(
            f"""
<div style='background:{_active_model_color};border:1px solid {_active_model_border};border-radius:8px;padding:10px 14px;margin-bottom:10px;'>
    <b style='color:{_active_model_text};'>Model used for this extraction run</b><br>
    <span style='font-size:0.9em;color:{_active_model_text};word-break:break-all;'>{_active_model_label}</span><br>
    <span style='font-size:0.85em;color:{_active_model_text};'>Escalation threshold: confidence &lt; 0.80</span>
</div>
""",
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader("Upload a ZIP file containing PDFs", type=["zip"])
        if uploaded_file:
            upload_id = getattr(uploaded_file, "id", None) or getattr(uploaded_file, "file_id", None) or ""
            upload_token = f"{uploaded_file.name}|{uploaded_file.size}|{upload_id}"
            if st.session_state.get('extraction_done_token') != upload_token:
                zip_bytes = uploaded_file.read()
                with st.spinner("Extracting documents, running inference, and logging results…"):
                    orch_result = ExtractionOrchestrationService.process_zip(zip_bytes)
                loan_package = orch_result["loan_package"]
                summary = orch_result["summary"]

                for fname, res in summary.items():
                    st.markdown(f"### {fname}")
                    st.markdown(f"<div style='background:#eaf6ff;padding:8px 0 8px 0;text-align:center;font-size:1.08em;font-weight:500;border-radius:8px;margin-bottom:8px;'>Document Type: <b>{res.get('doc_type', 'Unknown')}</b></div>", unsafe_allow_html=True)
                    # Display validation errors grouped in a card with icons
                    if res.get('errors'):
                        error_items = ""
                        for err in res['errors']:
                            # Icon for error type
                            if ' missing' in err:
                                icon = '⚠️'
                                base_field = err.split(' missing')[0].replace(' ', '_')
                            elif ' below confidence threshold' in err:
                                icon = '🔒'
                                base_field = err.split(' below confidence threshold')[0].replace(' ', '_')
                            else:
                                icon = '❗'
                                base_field = err.split(':')[0].replace(' ', '_')
                            confidence = res['field_confidences'].get(base_field, 'N/A')
                            if isinstance(confidence, float):
                                conf_str = f"{confidence:.2f}"
                            elif confidence == 'N/A':
                                conf_str = ''
                            else:
                                conf_str = str(confidence)
                            field_value = res['fields'].get(base_field, '')
                            if not field_value:
                                display_value = "<span style='color:#888'>(empty)</span>"
                            else:
                                display_value = f"{field_value}"
                            error_items += f"<li style='margin-bottom:8px;'><span style='font-size:1.2em'>{icon}</span> <b>{base_field}</b>: <span style='color:#d32f2f'>{err}</span><br>Value: {display_value} {'<br>Confidence: <b>' + conf_str + '</b>' if conf_str else ''}</li>"
                        st.markdown(f"""
<div style='background:#fff;border:1.5px solid #f8bdbd;padding:18px 18px 10px 18px;border-radius:14px;margin-bottom:24px;box-shadow:0 4px 16px #f8bdbd33;'>
<div style='background:#ffe0e0;padding:8px 0 8px 0;border-radius:8px;margin-bottom:12px;text-align:center;font-weight:600;font-size:1.08em;'>Validation Errors</div>
<ul style='padding-left:18px;margin-bottom:0;'>
{error_items}
</ul></div>
""", unsafe_allow_html=True)
                    # Show overall confidence as average of field confidences
                    field_confidences = list(res.get('field_confidences', {}).values())
                    if field_confidences:
                        avg_conf = sum([c for c in field_confidences if isinstance(c, float)]) / len([c for c in field_confidences if isinstance(c, float)])
                        st.markdown(f"<div style='background:#fff3e0;padding:8px;border-radius:8px;margin-bottom:8px;text-align:center;'><b>Overall Confidence:</b> {avg_conf:.2f}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='background:#fff3e0;padding:8px;border-radius:8px;margin-bottom:8px;text-align:center;'><b>Overall Confidence:</b> N/A</div>", unsafe_allow_html=True)
                st.session_state['extraction_done'] = uploaded_file.name
                st.session_state['extraction_done_token'] = upload_token
    with tabs[1]:
        st.markdown("""
<div style='background:#fff3e0;padding:8px 0 8px 0;text-align:center;font-size:1.08em;font-weight:500;border-radius:8px;margin-bottom:8px;'>
<b>Step 2: Error Detection & Escalation Review</b>
</div>
""", unsafe_allow_html=True)
        st.info(
            "Escalation Review decides if a flagged document can proceed now (Approve/Deny). "
            "Use Human Feedback to capture structured corrections for model learning."
        )
        import time
        pending_escalations = EscalationService.load_pending_escalations()
        reviewed_count = 0
        start_time = time.time()
        if not pending_escalations.empty:
            avg_review_time = (time.time() - start_time) / max(reviewed_count, 1)
            st.markdown(f"<div style='background:#e3f2fd;padding:8px 0 8px 0;text-align:center;font-size:1.05em;font-weight:500;border-radius:8px;margin-bottom:12px;'>Pending: <b>{len(pending_escalations)}</b> | Reviewed: <b>{reviewed_count}</b> | Average Review Time: <b>{avg_review_time:.2f} sec</b></div>", unsafe_allow_html=True)
            # Use session state to track reviewed documents (loan + prompt)
            if 'reviewed_docs' not in st.session_state:
                st.session_state['reviewed_docs'] = set()

            # Build pending list excluding already reviewed docs
            pending_list = []
            for idx, row in pending_escalations.iterrows():
                doc_key = f"{row['loan_package']}_{row['prompt']}"
                if doc_key not in st.session_state['reviewed_docs']:
                    pending_list.append((idx, row))

            if not pending_list:
                st.markdown("<div style='background:#e0e0e0;color:#888;font-size:1.1em;text-align:center;padding:16px;border-radius:12px;margin-bottom:18px;'>Nothing to review</div>", unsafe_allow_html=True)
            else:
                if 'current_escalation_idx' not in st.session_state:
                    st.session_state['current_escalation_idx'] = 0

                # Clamp index after reruns/reviews
                st.session_state['current_escalation_idx'] = min(
                    st.session_state['current_escalation_idx'],
                    len(pending_list) - 1
                )

                # Navigation controls
                st.markdown("<div style='text-align:center;margin-bottom:16px;'><b>Navigate Issues:</b></div>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns([1,2,1])
                with col1:
                    if st.button("Previous Issue"):
                        st.session_state['current_escalation_idx'] = max(0, st.session_state['current_escalation_idx'] - 1)
                with col3:
                    if st.button("Next Issue"):
                        st.session_state['current_escalation_idx'] = min(len(pending_list)-1, st.session_state['current_escalation_idx'] + 1)

                idx, row = pending_list[st.session_state['current_escalation_idx']]
                doc_key = f"{row['loan_package']}_{row['prompt']}"

                reason_text = str(row.get("reason", "")).strip()
                escalated_field = EscalationService.extract_escalated_field(reason_text)

                extracted_fields = {}
                response_text = row.get("response", "")
                if isinstance(response_text, str) and response_text.strip():
                    try:
                        parsed_response = json.loads(response_text)
                        if isinstance(parsed_response, dict):
                            extracted_fields = parsed_response
                    except Exception:
                        extracted_fields = {}

                escalated_value = ""
                if escalated_field:
                    escalated_value = str(extracted_fields.get(escalated_field, "")).strip()

                st.markdown(f"""
<div style='background:#f6fff8;border:1px solid #b7e4c7;padding:20px 20px 16px 20px;border-radius:14px;margin-bottom:20px;box-shadow:0 4px 16px #b7e4c733;width:100%;max-width:900px;margin-left:auto;margin-right:auto;'>
    <b style='font-size:1.15em;color:#1b5e20;'>Escalation Review</b><br>
    <div style='color:#1b5e20;font-size:1.02em;margin-top:12px;'>
        <b>Document:</b> {row['prompt']}<br>
        <b>Escalated Field:</b> {escalated_field if escalated_field else '(not detected)'}<br>
        <b>Current Extracted Value:</b> {escalated_value if escalated_value else '(empty)'}<br>
        <b>Reason:</b> {row['reason']}<br>
        <b>Confidence Score:</b> {row['confidence_score']}<br>
        <b>Risk Level:</b> {row['risk_level']}<br>
        <b>Decision:</b> {row['decision']}
    </div>
</div>
""", unsafe_allow_html=True)
                st.caption(
                    "Approve = accept the current extracted value for this escalated field. "
                    "Deny = reject it and require correction in Human Feedback."
                )
                escalated_pdf_path = os.path.join("sample_zips", "escalated", f"{row['loan_package']}_{row['prompt']}")
                if os.path.exists(escalated_pdf_path):
                    with open(escalated_pdf_path, "rb") as pdf_file:
                        st.download_button(label="Download Source Document", data=pdf_file.read(), file_name=row['prompt'], mime="application/pdf", key=f"download_{idx}")
                else:
                    st.markdown(f"<span style='color:#d32f2f;'>PDF not found for {row['prompt']}</span>", unsafe_allow_html=True)
                with st.form(key=f"review_form_{idx}"):
                    reviewer = st.selectbox(f"Reviewer name for {row['prompt']}", REVIEWER_NAMES, key=f"reviewer_{idx}")
                    action = st.selectbox(f"Decision for {row['prompt']}", ["Approve", "Deny"], key=f"action_{idx}")
                    comment_required = action == "Approve" and (float(row['confidence_score']) < 0.8 if row['confidence_score'] else False)
                    comment = st.text_area(f"Comment for {row['prompt']}", key=f"comment_{idx}")
                    submit_clicked = st.form_submit_button(f"Submit review for {row['prompt']}")
                    if submit_clicked:
                        if not reviewer:
                            st.error("Reviewer name is required.")
                        elif comment_required and not comment.strip():
                            st.error("Comment is required for approval of low confidence issues.")
                        else:
                            EscalationService.log_hil_action(row['timestamp'], reviewer, action, row['prompt'], row['loan_package'])
                            escalation_feedback_service = FeedbackService(log_dir="logs")
                            feedback_payload = EscalationService.build_governance_feedback_payload(
                                row,
                                action=action,
                                reviewer=reviewer,
                                comment=comment,
                                active_model_version=_active_model_version,
                                escalated_field=escalated_field,
                                escalated_value=escalated_value,
                            )
                            governance_result = escalation_feedback_service.submit_feedback(feedback_payload)
                            if not governance_result.get("success"):
                                st.warning(
                                    "Escalation decision was saved to HIL actions, but structured governance logging "
                                    "failed for this row."
                                )
                            reviewed_count += 1
                            # Mark all matching pending rows (same prompt and loan_package) as reviewed
                            for i, r in pending_escalations.iterrows():
                                if r['prompt'] == row['prompt'] and r['loan_package'] == row['loan_package']:
                                    match_key = f"{r['timestamp']}_{r['loan_package']}_{r['prompt']}"
                                    st.session_state.setdefault("reviewed_escalations", set()).add(match_key)
                            unique_key = f"{row['loan_package']}_{row['prompt']}"
                            st.session_state['just_reviewed'] = unique_key
                            st.success(f"Review submitted: {action} by {reviewer}")
                            st.rerun()
        else:
            st.markdown("<div style='background:#e0e0e0;color:#888;font-size:1.1em;text-align:center;padding:16px;border-radius:12px;margin-bottom:18px;'>Nothing to review</div>", unsafe_allow_html=True)
        # Escalation review logic
    with tabs[2]:
        st.markdown("""
<div style='background:#e8f5e9;padding:8px 0 8px 0;text-align:center;font-size:1.08em;font-weight:500;border-radius:8px;margin-bottom:8px;'>
<b>Step 3: Human Training Label Collection</b>
</div>
""", unsafe_allow_html=True)
        st.info(
            "Human Feedback captures what the model predicted versus what it should be for a specific document field. "
            "This tab writes structured labels for monitoring and retraining."
        )
        feedback_service = FeedbackService(log_dir="logs")

        escalation_logs = EscalationService.load_all_escalation_logs()
        if escalation_logs.empty:
            st.info("No escalated records found yet. Complete Step 1 and Step 2 first.")
        else:
            reviewed_logs = escalation_logs[
                escalation_logs["hil_action"].fillna("").astype(str).str.strip().str.lower().isin(["approve", "deny"])
            ]

            if reviewed_logs.empty:
                st.info("No reviewed escalations available for structured feedback yet.")
            else:
                reviewed_logs = reviewed_logs.copy()
                reviewed_logs["reason_text"] = reviewed_logs["reason"].fillna("").astype(str)
                reviewed_logs["escalated_field"] = reviewed_logs["reason_text"].apply(
                    EscalationService.extract_escalated_field
                )
                reviewed_logs["feedback_item_key"] = (
                    reviewed_logs["timestamp"].astype(str)
                    + "|"
                    + reviewed_logs["loan_package"].astype(str)
                    + "|"
                    + reviewed_logs["prompt"].astype(str)
                    + "|"
                    + reviewed_logs["escalated_field"].astype(str)
                )
                reviewed_logs = reviewed_logs[
                    ~reviewed_logs["feedback_item_key"].isin(st.session_state.get("submitted_human_feedback", set()))
                ]

                if reviewed_logs.empty:
                    st.markdown("<div style='background:#e0e0e0;color:#888;font-size:1.1em;text-align:center;padding:16px;border-radius:12px;margin-bottom:18px;'>No Human Feedback items pending</div>", unsafe_allow_html=True)
                else:
                    reviewed_logs["doc_key"] = (
                        reviewed_logs["loan_package"].astype(str)
                        + " | "
                        + reviewed_logs["prompt"].astype(str)
                        + " | field: "
                        + reviewed_logs["escalated_field"].replace("", "unknown_field")
                    )

                    selected_doc_key = st.selectbox(
                        "Reviewed document",
                        reviewed_logs["doc_key"].tolist(),
                        key="human_feedback_doc_key",
                    )
                    selected_row = reviewed_logs[reviewed_logs["doc_key"] == selected_doc_key].iloc[0]

                    parsed_fields = {}
                    response_value = selected_row.get("response", "")
                    if isinstance(response_value, str) and response_value.strip():
                        try:
                            loaded = json.loads(response_value)
                            if isinstance(loaded, dict):
                                parsed_fields = loaded
                        except Exception:
                            parsed_fields = {}

                    selected_field = str(selected_row.get("escalated_field", "")).strip() or "general"
                    predicted_value = str(parsed_fields.get(selected_field, "")) if parsed_fields else ""

                    st.markdown(
                    f"""
<div style='background:#f6fff8;border:1px solid #b7e4c7;padding:10px;border-radius:8px;margin-bottom:10px;'>
<b>Loan Package:</b> {selected_row.get('loan_package', '')}<br>
<b>Document:</b> {selected_row.get('prompt', '')}<br>
<b>Field:</b> {selected_field}<br>
<b>Current Model Value:</b> {predicted_value if predicted_value else '(empty)'}
</div>
""",
                        unsafe_allow_html=True,
                    )

                    escalated_pdf_path = os.path.join("sample_zips", "escalated", f"{selected_row.get('loan_package', '')}_{selected_row.get('prompt', '')}")
                    if os.path.exists(escalated_pdf_path):
                        with open(escalated_pdf_path, "rb") as pdf_file:
                            st.download_button(
                                label="Download source document for verification",
                                data=pdf_file.read(),
                                file_name=str(selected_row.get("prompt", "source.pdf")),
                                mime="application/pdf",
                                key=f"human_feedback_download_{selected_row.get('loan_package', '')}_{selected_row.get('prompt', '')}",
                            )

                    if not predicted_value:
                        st.warning(
                        "Current model value is empty. Do not guess. Check the source document: "
                        "enter a corrected value only if evidence is clear; otherwise use decision 'Cannot verify' "
                        "with reason 'insufficient_evidence'. Use 'missing_in_document' only when you confirmed "
                        "the field truly does not appear in the document."
                        )
                    elif predicted_value.strip().startswith("-"):
                        st.warning(
                        "Current model value is negative. Do not assume it should be positive. "
                        "Only select 'Does not match' when the source document clearly states a different value."
                        )

                    st.caption(
                    "Open the source document below, find this field, and compare it to the current model value. "
                    "Select whether the document matches, enter a correct value if it does not, or mark it unverifiable."
                    )

                    decision_options = ["matches_document", "does_not_match", "cannot_verify"]
                    decision_labels = {
                        "matches_document": "Matches document – the PDF shows the same value",
                        "does_not_match": "Does not match – the PDF shows a different value (enter it below)",
                        "cannot_verify": "Cannot verify – field is missing, illegible, or ambiguous in document",
                    }
                    reason_options = [
                    "verified",
                    "insufficient_evidence",
                    "missing_in_document",
                    "corrected_from_document",
                    "document_quality_issue",
                    ]

                    default_decision = "matches_document"
                    default_reason = "verified"
                    if not predicted_value:
                        default_decision = "cannot_verify"
                        default_reason = "insufficient_evidence"
                    elif predicted_value.strip().startswith("-"):
                        default_decision = "cannot_verify"
                        default_reason = "insufficient_evidence"

                    with st.form("human_feedback_submit_form"):
                        corrected_value = st.text_input("Correct value from document (only needed if 'Does not match')", value=predicted_value)
                        decision = st.selectbox(
                        "Does the source document match the model value?",
                        decision_options,
                        format_func=lambda x: decision_labels[x],
                        index=decision_options.index(default_decision),
                        key=f"human_feedback_decision_{selected_row.get('loan_package', '')}_{selected_row.get('prompt', '')}_{selected_field}",
                        )
                        reason_code = st.selectbox(
                        "Reason code (why)",
                        reason_options,
                        index=reason_options.index(default_reason),
                        key=f"human_feedback_reason_{selected_row.get('loan_package', '')}_{selected_row.get('prompt', '')}_{selected_field}",
                        )
                        comment = st.text_area("Reviewer comment (required when 'Does not match' — note the page/section in the document where you found the correct value)")
                        reviewer = st.selectbox("Reviewer", REVIEWER_NAMES, key="human_feedback_reviewer")
                        model_version = st.text_input("Model version", value=_active_model_version, disabled=True)
                        run_id = st.text_input(
                        "Run ID",
                        value=f"{selected_row.get('loan_package', '')}_{selected_row.get('timestamp', '')}",
                        )

                        if not predicted_value:
                            st.caption(
                            "Recommended: Cannot verify + insufficient_evidence unless the source document clearly shows a value. "
                            "If the field is confirmed absent from the document, use missing_in_document."
                            )
                        elif predicted_value.strip().startswith("-"):
                            st.caption(
                            "Recommended: Cannot verify until you confirm what the document actually shows for this field. "
                            "If the document shows the same negative value, select 'Matches document'."
                            )

                        submitted = st.form_submit_button("Submit feedback")
                        if submitted:
                            package_id = str(selected_row.get("loan_package", "")).strip()
                            document_name = str(selected_row.get("prompt", "")).strip()
                            document_type = EscalationService.normalize_document_type(document_name)
                            submit_allowed = True

                            if not predicted_value and not corrected_value and decision != "cannot_verify":
                                st.error(
                                "For empty model values, either enter the correct value from the source document "
                                "or choose 'Cannot verify' with reason 'insufficient_evidence'."
                                )
                                submit_allowed = False

                            if decision == "does_not_match" and not corrected_value.strip():
                                st.error("Enter the correct value from the document when selecting 'Does not match'.")
                                submit_allowed = False

                            if submit_allowed:
                                payload = {
                                    "package_id": package_id,
                                    "loan_package": package_id,
                                    "document_type": document_type,
                                    "field_name": selected_field,
                                    "model_prediction": predicted_value,
                                    "corrected_value": corrected_value,
                                    "decision": decision,
                                    "reason_code": reason_code,
                                    "comment": comment,
                                    "reviewer": reviewer,
                                    "model_version": model_version,
                                    "run_id": run_id,
                                    "source_tab": "human_feedback",
                                }

                                result = feedback_service.submit_feedback(payload)
                                if not result.get("success"):
                                    for error in result.get("errors", []):
                                        st.error(error)
                                elif result.get("duplicate"):
                                    st.warning("Duplicate feedback detected. Existing entry retained.")
                                else:
                                    item_key = str(selected_row.get("feedback_item_key", "")).strip()
                                    if item_key:
                                        st.session_state.setdefault("submitted_human_feedback", set()).add(item_key)
                                    st.success("Feedback submitted and logged.")
                                    st.rerun()

    with tabs[3]:
        st.markdown("""
<div style='background:#e3f2fd;padding:8px 0 8px 0;text-align:center;font-size:1.08em;font-weight:500;border-radius:8px;margin-bottom:8px;'>
<b>Step 4: Model Monitoring & Effectiveness</b>
</div>
""", unsafe_allow_html=True)

        st.info(
            "This tab shows how human feedback is accumulating and lets you retrain the field validation model "
            "with human-verified ground truth labels. Retraining uses only 'Matches document' and 'Does not match' "
            "decisions from the Human Feedback tab."
        )

        # ── Feedback readiness metrics ─────────────────────────────────────
        feedback_service = FeedbackService(log_dir="logs")
        summary = feedback_service.feedback_summary(filters={"source_tab": "human_feedback"})
        by_decision = summary.get("by_decision", {})

        st.markdown("### Feedback Readiness")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Human Feedback", summary.get("total", 0))
        col2.metric("Matches Document", by_decision.get("matches_document", 0))
        col3.metric("Does Not Match", by_decision.get("does_not_match", 0))
        col4.metric("Cannot Verify", by_decision.get("cannot_verify", 0))

        pending_filters = ModelMonitoringService.get_pending_label_filters(MANIFEST_PATH)
        export_preview = feedback_service.export_training_labels(filters=pending_filters)
        eligible = export_preview.get("total_exported_labels", 0)
        skipped = export_preview.get("skipped", {})

        st.markdown("##### Training Label Export Preview")
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Pending Training Labels", eligible, help="New labels since last retrain with known ground truth: Matches document + Does not match")
        col_b.metric("Skipped – Cannot Verify", skipped.get("ineligible_decision", 0))
        col_c.metric("Skipped – Duplicates", skipped.get("duplicates", 0))
        st.caption(
            "Pending training labels are NEW feedback rows since the last retrain where we know the correct answer "
            "from the source document. 'Cannot verify' is excluded because no ground truth label is available."
        )

        if eligible == 0:
            st.warning(
                "No eligible training labels yet. Submit Human Feedback with 'Matches document' or "
                "'Does not match' decisions to generate ground-truth labels for retraining."
            )
            st.caption("Retrain button is disabled until at least 1 training-eligible label exists.")

        # ── Last retrain manifest ──────────────────────────────────────────
        history = ModelMonitoringService.load_manifest(MANIFEST_PATH)
        if history:
            history = ModelMonitoringService.enrich_history(history)
            st.markdown("### KPI Snapshot (What Matters)")
            latest_kpi = history[-1]
            previous_kpi = history[-2] if len(history) > 1 else None
            outcome_label, outcome_text, outcome_bg, outcome_reason = ModelMonitoringService.retrain_outcome(latest_kpi, previous_kpi)
            pending_ratio = 0.0
            if summary.get("total", 0):
                pending_ratio = (eligible / summary.get("total", 0)) * 100

            escalation_logs_kpi = EscalationService.load_all_escalation_logs()
            total_escalations_kpi = len(escalation_logs_kpi) if escalation_logs_kpi is not None else 0
            reviewed_escalations_kpi = 0
            if escalation_logs_kpi is not None and not escalation_logs_kpi.empty and "hil_action" in escalation_logs_kpi.columns:
                reviewed_escalations_kpi = int(
                    escalation_logs_kpi["hil_action"].fillna("").astype(str).str.strip().str.lower().isin(["approve", "deny"]).sum()
                )

            k1, k2, k3, k4 = st.columns(4)
            invalid_recall_val = latest_kpi.get("invalid_recall")
            macro_f1_val = latest_kpi.get("macro_f1")
            k1.metric(
                "Invalid Recall (Class 0)",
                f"{round(float(invalid_recall_val) * 100, 1)}%" if invalid_recall_val is not None else "N/A"
            )
            k2.metric(
                "Macro F1",
                f"{round(float(macro_f1_val) * 100, 1)}%" if macro_f1_val is not None else "N/A"
            )
            k3.metric("Escalation Review Rate", f"{round((reviewed_escalations_kpi / total_escalations_kpi) * 100, 1) if total_escalations_kpi else 0}%")
            k4.metric("Pending Label Ratio", f"{round(pending_ratio, 1)}%")

            st.markdown(
                f"""
<div style='background:{outcome_bg};border:1px solid {outcome_text};border-radius:8px;padding:10px 14px;margin:8px 0 14px 0;'>
    <b style='color:{outcome_text};'>Retrain Outcome:</b>
    <span style='color:{outcome_text};font-weight:600;'>{outcome_label}</span><br>
    <span style='color:{outcome_text};font-size:0.9em;'>{outcome_reason}</span>
</div>
""",
                unsafe_allow_html=True,
            )

            last = history[-1]
            st.markdown("### Last Retrain Run")
            st.markdown(f"""
<div style='background:#f6fff8;border:1px solid #b7e4c7;border-radius:8px;padding:12px 16px;color:#1b5e20;margin-bottom:8px;'>
<b>Retrained at:</b> {last.get('retrained_at','—')}<br>
<b>Model version:</b> {last.get('model_version','—')}<br>
<b>Outcome:</b> {outcome_label}<br>
<b>Model file:</b> {last.get('model_file','—')}<br>
<b>Base records:</b> {last.get('base_records','—')} &nbsp;|&nbsp;
<b>New records added:</b> {last.get('new_training_records_added','—')} &nbsp;|&nbsp;
<b>Augmented total:</b> {last.get('total_augmented_records','—')}<br>
<b>Test accuracy:</b> {round(last.get('test_set_accuracy', 0) * 100, 1)}% &nbsp;|&nbsp;
<b>Invalid recall:</b> {f"{round(float(last.get('invalid_recall')) * 100, 1)}%" if last.get('invalid_recall') is not None else 'N/A'} &nbsp;|&nbsp;
<b>Macro F1:</b> {f"{round(float(last.get('macro_f1')) * 100, 1)}%" if last.get('macro_f1') is not None else 'N/A'}
</div>
""", unsafe_allow_html=True)
            with st.expander("Classification report"):
                st.text(last.get("classification_report", ""))
            if len(history) > 1:
                st.caption(f"{len(history)} total retrain runs recorded in manifest.")
                trend_rows = ModelMonitoringService.build_trend_dataframe(history)
                trend_df = pd.DataFrame(trend_rows)
                st.markdown("### Retrain Performance by Model Version")
                st.line_chart(trend_df.set_index("model_version")[["accuracy", "invalid_recall", "macro_f1"]])
                st.dataframe(trend_df.sort_values("run", ascending=False), use_container_width=True)

        # ── Retrain button ─────────────────────────────────────────────────
        st.markdown("### Retrain Model")
        st.markdown(
            "Augments the base training dataset with human-verified labels and trains a new "
            "RandomForest field validation model. The original dataset is never modified — "
            "a separate augmented copy is saved alongside the new model."
        )

        st.markdown("### Reset for Demo")
        st.caption(
            "Need to re-run the full before/after demo? Reset active model to baseline v0.11.1 so "
            "negative-balance cases escalate again before retraining."
        )
        reset_history = st.checkbox("Start fresh demo history (clear retrain manifest)", value=False)
        if st.button("Reset Active Model to Baseline (v0.11.1)"):
            with st.spinner("Rebuilding baseline model and updating active deployment model…"):
                reset_result = reset_active_model_to_baseline(reset_manifest=reset_history)
            if not reset_result.get("success"):
                st.error(f"Baseline reset failed: {reset_result.get('error')}")
            else:
                st.success(
                    "Active model reset to baseline v0.11.1. "
                    "Run extraction again to demonstrate baseline escalation, then submit feedback and retrain."
                )
                st.rerun()

        label_weight = st.slider(
            "Human label weight (×)",
            min_value=1, max_value=50, value=10,
            help=(
                "Each human-verified label is replicated this many times in the training set. "
                "With ~437 base records, a weight of 10 gives each human label roughly 10× the "
                "influence of a base record — enough to shift model confidence past 0.8 after "
                "a single feedback submission. Increase if confidence still doesn't move."
            ),
        )

        if st.button("Retrain with Human Feedback", disabled=(eligible == 0), type="primary"):
            with st.spinner("Exporting labels, augmenting dataset, training model…"):
                result = retrain_with_feedback(label_weight=label_weight)

            if not result.get("success"):
                st.error(f"Retraining failed: {result.get('error')}")
            else:
                st.success(
                    f"Model retrained successfully. "
                    f"New model version: {result['model_version']}. "
                    f"{result['new_records']} unique human labels × {result['label_weight']} weight "
                    f"= {result['weighted_records']} records added. "
                    f"Augmented dataset: {result['augmented_records']} total records. "
                    f"Active model updated."
                )
                col_x, col_y = st.columns(2)
                col_x.markdown(f"**Active model updated:**  \n`field_validation_rf_encoded_model.joblib` ({result['model_version']})")
                col_y.markdown(f"**Timestamped backup:**  \n`{os.path.basename(result['model_path'])}`")

                accuracy = result.get("metrics", {}).get("accuracy", 0)
                st.metric("Test Set Accuracy", f"{round(accuracy * 100, 1)}%")

                with st.expander("Full classification report"):
                    st.text(result["classification_report"])

                st.rerun()

    with tabs[4]:
        st.markdown("""
<div style='background:#fff8e1;padding:8px 0 8px 0;text-align:center;font-size:1.08em;font-weight:500;border-radius:8px;margin-bottom:8px;'>
<b>Governance & Audit Review</b>
</div>
""", unsafe_allow_html=True)

        st.info(
            "All human feedback submitted via the Human Feedback tab. "
            "Use this view to audit decisions, spot patterns, and understand what is going into the training loop."
        )

        fb_service = FeedbackService()
        fb_summary = fb_service.feedback_summary(filters={"source_tab": "human_feedback"})
        fb_by_decision = fb_summary.get("by_decision", {})

        st.markdown("### Summary")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Submitted", fb_summary.get("total", 0))
        col2.metric("Matches Document", fb_by_decision.get("matches_document", 0))
        col3.metric("Does Not Match", fb_by_decision.get("does_not_match", 0))
        col4.metric("Cannot Verify", fb_by_decision.get("cannot_verify", 0))

        fb_export = fb_service.export_training_labels()
        st.caption(
            f"Training-eligible labels: **{fb_export.get('total_exported_labels', 0)}** "
            f"('Matches document' + 'Does not match' decisions only — 'Cannot verify' is excluded "
            f"because no ground truth is known). "
            f"Skipped: {fb_export.get('skipped', {}).get('ineligible_decision', 0)} ineligible, "
            f"{fb_export.get('skipped', {}).get('duplicates', 0)} duplicates."
        )

        st.markdown("### All Feedback Records")
        all_feedback = fb_service.list_feedback(filters={"source_tab": "human_feedback"})
        if all_feedback:
            fb_df = pd.DataFrame(all_feedback)
            display_cols = [c for c in ["timestamp", "loan_package", "document_type", "field_name",
                                        "model_prediction", "corrected_value", "decision",
                                        "reason_code", "comment", "reviewer", "model_version"] if c in fb_df.columns]
            st.dataframe(fb_df[display_cols], use_container_width=True)

            csv_bytes = fb_df.to_csv(index=False).encode()
            st.download_button(
                "Download feedback log as CSV",
                data=csv_bytes,
                file_name="feedback_log_export.csv",
                mime="text/csv",
            )
        else:
            st.info("No human feedback submitted yet.")

        st.markdown("---")
        st.markdown("### Escalation Review History (Governance)")

        governance_reviews = fb_service.list_feedback(filters={"source_tab": "escalation_review"})
        governance_df = pd.DataFrame(governance_reviews) if governance_reviews else pd.DataFrame()

        current_escalations = EscalationService.load_all_escalation_logs()
        pending_escalations = EscalationService.load_pending_escalations()
        total_escalations = len(current_escalations) if current_escalations is not None and not current_escalations.empty else 0
        pending_count = len(pending_escalations) if pending_escalations is not None and not pending_escalations.empty else 0

        if not governance_df.empty:
            governance_df["decision"] = governance_df["decision"].fillna("").astype(str).str.strip().str.lower()
            reviewed_escalations = governance_df[
                governance_df["decision"].isin(["approve", "deny"])
            ].copy()
            approved_count = int((reviewed_escalations["decision"] == "approve").sum()) if not reviewed_escalations.empty else 0
            denied_count = int((reviewed_escalations["decision"] == "deny").sum()) if not reviewed_escalations.empty else 0

            ec1, ec2, ec3, ec4 = st.columns(4)
            ec1.metric("Governance Reviews", len(reviewed_escalations))
            ec2.metric("Approved", approved_count)
            ec3.metric("Denied", denied_count)
            ec4.metric("Current Pending", pending_count)
            st.caption(f"Current-session escalations in interaction log: {total_escalations}")

            review_cols = [
                c for c in [
                    "timestamp",
                    "loan_package",
                    "document_type",
                    "field_name",
                    "model_prediction",
                    "decision",
                    "reason_code",
                    "comment",
                    "reviewer",
                    "model_version",
                ] if c in reviewed_escalations.columns
            ]
            st.dataframe(
                reviewed_escalations[review_cols].sort_values("timestamp", ascending=False),
                use_container_width=True,
            )

            escalation_csv = reviewed_escalations.to_csv(index=False).encode()
            st.download_button(
                "Download escalation review history as CSV",
                data=escalation_csv,
                file_name="escalation_review_history.csv",
                mime="text/csv",
            )
        else:
            ec1, ec2 = st.columns(2)
            ec1.metric("Governance Reviews", 0)
            ec2.metric("Current Pending", pending_count)
            st.info("No structured escalation-review decisions have been logged yet.")

__all__ = ["main"]
if __name__ == '__main__':
    main()