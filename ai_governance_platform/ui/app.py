import os
import glob
import re
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from ai_governance_platform.services.extraction_service import extract_and_validate
from ai_governance_platform.services.evaluation_service import EvaluationService
from ai_governance_platform.services.escalation_service import EscalationService
import zipfile
import io
import json
        
class LoanApplication:
    def __init__(self, applicant_name, property_address, loan_amount, interest_rate, term_years, signature):
        self.applicant_name = applicant_name
        self.property_address = property_address
        self.loan_amount = loan_amount
        self.interest_rate = interest_rate
        self.term_years = term_years
        self.signature = signature

class Disclosure:
    def __init__(self, disclosure_date, loan_terms, interest_rate, fees, signature):
        self.disclosure_date = disclosure_date
        self.loan_terms = loan_terms
        self.interest_rate = interest_rate
        self.fees = fees
        self.signature = signature

class CreditReport:
    def __init__(self, applicant_name, credit_score, report_date, accounts, signature):
        self.applicant_name = applicant_name
        self.credit_score = credit_score
        self.report_date = report_date
        self.accounts = accounts
        self.signature = signature

class AppraisalReport:
    def __init__(self, property_address, appraised_value, appraiser_name, date, signature):
        self.property_address = property_address
        self.appraised_value = appraised_value
        self.appraiser_name = appraiser_name
        self.date = date
        self.signature = signature

class IncomeVerification:
    def __init__(self, applicant_name, employer, income, tax_year, signature):
        self.applicant_name = applicant_name
        self.employer = employer
        self.income = income
        self.tax_year = tax_year
        self.signature = signature

class BankStatement:
    def __init__(self, account_holder, account_number, balance, statement_date, signature):
        self.account_holder = account_holder
        self.account_number = account_number
        self.balance = balance
        self.statement_date = statement_date
        self.signature = signature

class TaxReturn:
    def __init__(self, taxpayer_name, year, income, deductions, signature):
        self.taxpayer_name = taxpayer_name
        self.year = year
        self.income = income
        self.deductions = deductions
        self.signature = signature

class ClosingDocuments:
    def __init__(self, closing_date, property_address, loan_amount, buyer, seller, signature):
        self.closing_date = closing_date
        self.property_address = property_address
        self.loan_amount = loan_amount
        self.buyer = buyer
        self.seller = seller
        self.signature = signature

# ...existing code...

def _init_session_state():
    st.session_state.setdefault("reviewed_escalations", set())
    st.session_state.setdefault("current_escalation_idx", 0)

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
    st.sidebar.markdown("""
<div style='background:#eaf6ff;border:1.5px solid #b3e5fc;padding:10px 12px 8px 12px;margin-bottom:12px;text-align:center;border-radius:8px;'>
<span style='font-size:1.08em;font-weight:600;color:#1976d2;'>App version:</span><br>
v0.10.0 - Modular workflow, robust UI, document extraction, validation, escalation, feedback, and monitoring
</div>
""", unsafe_allow_html=True)
    st.sidebar.markdown("""
<div class='sidebar-card' style='background:#eaf6ff;font-size:0.93em;margin-bottom:16px;border:1.5px solid #b3e5fc;padding:8px 8px 6px 8px;'>
<div style='font-weight:700;font-size:1em;line-height:1.2;margin-bottom:2px;text-align:center;'>
<span style="font-size:1.05em;vertical-align:middle;">&#129302;</span> AI Governance & Evaluation Platform v0.10.0
</div>
<div style='margin:0 0 0 0;font-size:0.91em;line-height:1.35;text-align:center;'>
<span style="font-size:1em;">&#128221;</span> <span>Audit Logging for all AI interactions</span>
</div>
<div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
<span style="font-size:1em;">&#9878;</span> <span>Policy Engine for query risk assessment</span>
</div>
<div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
<span style="font-size:1em;">&#128172;</span> <span>Feedback logging and summary</span>
</div>
<div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
<span style="font-size:1em;">&#128721;</span> <span>Escalation Review & Human-in-the-Loop (HIL) for low-confidence or high-risk documents</span>
</div>
<div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
<span style="font-size:1em;">&#128200;</span> <span>System Health KPIs and metrics</span>
</div>
<div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
<span style="font-size:1em;">&#128196;</span> <span>Document Extraction, Validation, and Confidence Scoring</span>
</div>
<div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
<span style="font-size:1em;">&#128451;</span> <span>Audit Log Tab & Sequential Loan Numbering</span>
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
    This platform enables safe, observable, and governed AI operations for enterprise environments. It features modular business logic, real-time escalation review, document extraction and validation, audit logging, feedback collection, and system health metrics. Designed for CTOs, CEOs, hiring managers, and PE operators.

    **Target Audience:**
    Executives, engineering leaders, HR, private equity operators, and technical decision-makers seeking robust AI governance, auditability, and evaluation for enterprise AI systems.

    **Key Features:**
    - Audit Logging for all AI interactions
    - Policy Engine for query risk assessment
    - Feedback logging and summary
    - Escalation Review & Human-in-the-Loop (HIL) for low-confidence or high-risk documents
    - System Health KPIs and metrics
    - Document Extraction, Validation, and Confidence Scoring
    - Audit Log Tab & Sequential Loan Numbering
    - Streamlit-based modern UI
    - Open-source, modular Python codebase
    """, unsafe_allow_html=True)

    with st.sidebar.expander("&#128193; Project Documentation", expanded=False):
        st.markdown("**Project Documentation**")
        st.markdown("<span style='font-size:1.05em;'>🌐</span> [GitHub Repository](https://github.com/obizues/AI-Governance-Platform)", unsafe_allow_html=True)
        st.markdown("- <span style='font-size:1.05em;'>📘</span> [README.md](https://github.com/obizues/AI-Governance-Platform/blob/main/README.md): Project overview, setup, features", unsafe_allow_html=True)
        st.markdown("- <span style='font-size:1.05em;'>📝</span> [CHANGELOG.md](https://github.com/obizues/AI-Governance-Platform/blob/main/CHANGELOG.md): Release notes and updates", unsafe_allow_html=True)
        st.markdown("- <span style='font-size:1.05em;'>🗂️</span> [System Architecture](https://github.com/obizues/AI-Governance-Platform/blob/main/docs/architecture.md): Design and flow diagrams", unsafe_allow_html=True)
        st.markdown("**Key Sections:**\n- Modular business logic\n- Audit Logging\n- Policy Engine\n- Feedback & Evaluation\n- System Health KPIs\n- Deployment & Usage Guide")

    with st.sidebar.expander("&#128295; Tech Stack", expanded=False):
        st.markdown("""
<span style='font-size:1em;'>
<ul style='margin-bottom:0; padding-left: 18px;'>
<li>Python 3.10+</li>
<li>Streamlit (UI)</li>
<li>pandas, pdfplumber (data extraction)</li>
<li>Modular service architecture</li>
<li>YAML for policy configuration</li>
<li>Pytest for testing</li>
</ul>
""", unsafe_allow_html=True)

    with st.sidebar.expander("📝 System Design Notes", expanded=False):
        st.markdown("""
**Key architectural decisions**
<li><b>All business logic is modularized in services/</b></li>
<li><b>Centralized config/, data/, and logs/ folders</b></li>
<li><b>UI is decoupled from core logic</b></li>
<li><b>Policy rules in config/policy.yaml</b></li>
<li><b>Feedback loop via services/feedback_service.py</b></li>
<li><b>KPIs and metrics via services/metrics_service.py</b></li>
<li><b>Deployment:</b> Streamlit Cloud, local, or containerized environments.</li>
<li><b>Demo Files:</b> Sidebar expander with download buttons, dynamic listing of sample files for testing.</li>
<li><b>UI/UX:</b> Improved sidebar layout, banners, and tabbed navigation.</li>
""", unsafe_allow_html=True)
    # ...existing code...
    tabs = st.tabs(["Extraction & Validation", "Escalation Review", "Human Feedback", "Model Monitoring"])
    with tabs[0]:
        st.markdown("""
<div style='background:#eaf6ff;padding:8px 0 8px 0;text-align:center;font-size:1.08em;font-weight:500;border-radius:8px;margin-bottom:8px;'>
<b>Step 1: Document Extraction & Validation</b>
</div>
""", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload a ZIP file containing PDFs", type=["zip"])
        if uploaded_file:
            if 'extraction_done' not in st.session_state or st.session_state['extraction_done'] != uploaded_file.name:
                # Clear history
                ai_interactions_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs', 'ai_interactions.csv'))
                import csv
                with open(ai_interactions_path, 'w', newline='') as csvfile:
                    fieldnames = [
                        "timestamp", "user_role", "loan_package", "prompt", "response", "response_time_ms",
                        "confidence_score", "risk_level", "decision", "rule_triggered", "reason",
                        "required_controls", "hil_action", "hil_reviewer"
                    ]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                import datetime
                import uuid
                import os
                import zipfile
                import io
                loan_package = str(uuid.uuid4())[:8]
                pdf_output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'sample_zips', loan_package))
                os.makedirs(pdf_output_dir, exist_ok=True)
                zip_bytes = uploaded_file.read()
                with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
                    pdf_files = [f for f in z.namelist() if f.lower().endswith('.pdf')]
                    summary = {}
                    for pdf_name in pdf_files:
                        pdf_bytes = z.read(pdf_name)
                        result = extract_and_validate(pdf_bytes)
                        expected_keywords = list(result.get('fields', {}).keys())
                        eval_service = EvaluationService(dataset_path='ai_governance_platform/data/evaluation_dataset.json', report_path='ai_governance_platform/data/evaluation_report.json')
                        import joblib
                        import sys
                        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
                        if script_path not in sys.path:
                            sys.path.append(script_path)
                        from predict_field_validation import load_model, predict_validity
                        model_path = 'ai_governance_platform/models/field_validation_rf_encoded_model.joblib'
                        model = load_model(model_path)
                        model_features = ['is_empty', 'is_negative', 'is_nonsensical', 'is_out_of_range', 'field_encoded', 'doc_type_encoded']
                        field_confidences = {}
                        for field, value in result.get('fields', {}).items():
                            pred, prob = predict_validity(model, model_features, field, value, result.get('doc_type', 'Unknown'))
                            field_confidences[field] = prob
                        result['field_confidences'] = field_confidences
                        CONFIDENCE_THRESHOLD = 0.8
                        escalate_fields = [field for field, conf in field_confidences.items() if isinstance(conf, float) and conf < CONFIDENCE_THRESHOLD]
                        escalate = bool(escalate_fields)
                        for field, conf in field_confidences.items():
                            if isinstance(conf, float) and conf < CONFIDENCE_THRESHOLD:
                                error_msg = f"{field.replace('_', ' ')} below confidence threshold ({conf:.2f})"
                                if 'errors' in result:
                                    result['errors'].append(error_msg)
                                else:
                                    result['errors'] = [error_msg]
                        summary[pdf_name] = result
                        now = datetime.datetime.now().isoformat()
                        # Log each field needing review as a separate escalation row
                        if escalate:
                            for field in escalate_fields:
                                row = {
                                    "timestamp": now,
                                    "user_role": "system",
                                    "loan_package": loan_package,
                                    "prompt": pdf_name,
                                    "response": json.dumps(result['fields']),
                                    "response_time_ms": "",
                                    "confidence_score": f"{field_confidences[field]:.2f}",
                                    "risk_level": "high",
                                    "decision": "escalate",
                                    "rule_triggered": "escalate",
                                    "reason": f"{field.replace('_', ' ')} below confidence threshold ({field_confidences[field]:.2f})",
                                    "required_controls": "",
                                    "hil_action": "",
                                    "hil_reviewer": ""
                                }
                                with open(ai_interactions_path, 'a', newline='') as csvfile:
                                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                                    writer.writerow(row)
                            # Save PDF only if escalated
                            escalated_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'sample_zips', 'escalated'))
                            os.makedirs(escalated_dir, exist_ok=True)
                            pdf_path = os.path.join(escalated_dir, f"{loan_package}_{pdf_name}")
                            with open(pdf_path, 'wb') as f:
                                f.write(pdf_bytes)
                        else:
                            # Log non-escalated document as a single row
                            row = {
                                "timestamp": now,
                                "user_role": "system",
                                "loan_package": loan_package,
                                "prompt": pdf_name,
                                "response": json.dumps(result['fields']),
                                "response_time_ms": "",
                                "confidence_score": f"{sum([c for c in field_confidences.values() if isinstance(c, float)]) / len([c for c in field_confidences.values() if isinstance(c, float)]) if field_confidences else 0:.2f}",
                                "risk_level": "low",
                                "decision": "approve",
                                "rule_triggered": "",
                                "reason": ", ".join(result.get('errors', [])),
                                "required_controls": "",
                                "hil_action": "",
                                "hil_reviewer": ""
                            }
                            with open(ai_interactions_path, 'a', newline='') as csvfile:
                                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                                writer.writerow(row)
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
    with tabs[1]:
        st.markdown("""
<div style='background:#fff3e0;padding:8px 0 8px 0;text-align:center;font-size:1.08em;font-weight:500;border-radius:8px;margin-bottom:8px;'>
<b>Step 2: Error Detection & Escalation Review</b>
</div>
""", unsafe_allow_html=True)
        from ai_governance_platform.services.escalation_service import EscalationService
        import time
        pending_escalations = EscalationService.load_pending_escalations()
        reviewed_count = 0
        reviewer_names = ["Alice Smith", "Bob Johnson", "Chris Obermeier", "Dana Lee", "Evan Kim"]
        start_time = time.time()
        if not pending_escalations.empty:
            st.markdown("<div style='background:#fff8e1;border:1.5px solid #ffd54f;padding:18px 18px 10px 18px;border-radius:14px;margin-bottom:24px;box-shadow:0 4px 16px #ffd54f33;text-align:center;font-size:1.1em;font-weight:600;'>Escalated Issues Pending Review</div>", unsafe_allow_html=True)
            avg_review_time = (time.time() - start_time) / max(reviewed_count, 1)
            st.markdown(f"<div style='background:#e3f2fd;padding:8px 0 8px 0;text-align:center;font-size:1.05em;font-weight:500;border-radius:8px;margin-bottom:12px;'>Pending: <b>{len(pending_escalations)}</b> | Reviewed: <b>{reviewed_count}</b> | Average Review Time: <b>{avg_review_time:.2f} sec</b></div>", unsafe_allow_html=True)
            import streamlit as st
            import time
            from ai_governance_platform.services.escalation_service import EscalationService
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
                st.markdown(f"""
<div style='background:#1976d2;border:2px solid #1976d2;padding:32px 32px 24px 32px;border-radius:24px;margin-bottom:32px;box-shadow:0 6px 24px #1976d233;width:100%;max-width:900px;margin-left:auto;margin-right:auto;'>
    <b style='font-size:1.25em;color:#fff;'>Escalation Review</b><br>
    <div style='color:#fff;font-size:1.08em;margin-top:12px;'>
        <b>Document:</b> {row['prompt']}<br>
        <b>Reason:</b> {row['reason']}<br>
        <b>Confidence Score:</b> {row['confidence_score']}<br>
        <b>Risk Level:</b> {row['risk_level']}<br>
        <b>Decision:</b> {row['decision']}
    </div>
</div>
""", unsafe_allow_html=True)
                escalated_pdf_path = os.path.join("sample_zips", "escalated", f"{row['loan_package']}_{row['prompt']}")
                if os.path.exists(escalated_pdf_path):
                    with open(escalated_pdf_path, "rb") as pdf_file:
                        st.download_button(label="Download Source Document", data=pdf_file.read(), file_name=row['prompt'], mime="application/pdf", key=f"download_{idx}")
                else:
                    st.markdown(f"<span style='color:#d32f2f;'>PDF not found for {row['prompt']}</span>", unsafe_allow_html=True)
                with st.form(key=f"review_form_{idx}"):
                    reviewer = st.selectbox(f"Reviewer name for {row['prompt']}", reviewer_names, key=f"reviewer_{idx}")
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
<b>Step 3: Human Feedback Collection</b>
</div>
""", unsafe_allow_html=True)
        # Human feedback logic
    with tabs[3]:
        st.markdown("""
<div style='background:#e3f2fd;padding:8px 0 8px 0;text-align:center;font-size:1.08em;font-weight:500;border-radius:8px;margin-bottom:8px;'>
<b>Step 4: Model Monitoring & Effectiveness</b>
</div>
""", unsafe_allow_html=True)
        # Model monitoring logic

__all__ = ["main"]
if __name__ == '__main__':
    main()