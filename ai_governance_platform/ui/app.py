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
import yaml
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "logs", "ai_interactions.csv"))
FEEDBACK_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "logs", "feedback_log.csv"))
FEEDBACK_SUMMARY_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "logs", "feedback_summary.json"))
POLICY_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "policy", "policy.yaml"))

st.sidebar.markdown("""
<div style='background:#eaf6ff;border:1.5px solid #b3e5fc;padding:10px 12px 8px 12px;margin-bottom:12px;text-align:center;border-radius:8px;'>
    <span style='font-size:1.08em;font-weight:600;color:#1976d2;'>App version:</span><br>
    <span style='font-size:1.05em;color:#222;'>v0.6.0 - Real-time Escalation Sync, Human Review Workflow, Document Extraction & Validation, Audit Log Tab, Sequential Loan Numbering, UI/UX Improvements</span>
</div>
<div class='sidebar-card' style='background:#eaf6ff;font-size:0.93em;margin-bottom:16px;border:1.5px solid #b3e5fc;padding:8px 8px 6px 8px;'>
    <div style='font-weight:700;font-size:1em;line-height:1.2;margin-bottom:2px;text-align:center;'>
        <span style="font-size:1.05em;vertical-align:middle;">🤖</span> AI Governance & Evaluation Platform v0.6.0
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
            <span style="font-size:1em;">🛑</span> <span>Escalation Review & Human-in-the-Loop (HIL) for low-confidence or high-risk documents</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">📊</span> <span>System Health KPIs and metrics</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">📄</span> <span>Document Extraction, Validation, and Confidence Scoring</span>
        </div>
        <div style='display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:2px;'>
            <span style="font-size:1em;">🗂️</span> <span>Audit Log Tab & Sequential Loan Numbering</span>
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
- Real-time escalation sync and human review workflow
- Document extraction, validation, and confidence scoring
- Audit log tab with full review history
- Sequential loan numbering and improved UI/UX
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
""", unsafe_allow_html=True)

    with st.sidebar.expander("📝 System Design Notes", expanded=False):
        st.markdown("""
    **Key architectural decisions**
    <li><b>Feedback Logging:</b> User feedback is logged and summarized for continuous improvement.</li>
    <li><b>System Health KPIs:</b> Real-time metrics for queries, deny rate, escalation, latency, trust score, and feedback.</li>
    <li><b>Streamlit UI:</b> Modern, business-focused interface with tabs for queries, feedback, health, and escalation review.</li>
    <li><b>Open Source:</b> Extensible Python codebase, GitHub-hosted, CI/CD enabled.</li>
    <li><b>Deployment:</b> Streamlit Cloud, local, or containerized environments.</li>
    """, unsafe_allow_html=True)
"""

"""
# --- Top blue app title bar (centered, above personal info) ---
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
</style>
<div class="main-title-banner">
    <span class="emoji">🤖</span> AI Governance & Evaluation Platform
</div>
""", unsafe_allow_html=True)

# --- Personal Information Banner ---
personal_info_banner = """
<style>
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

st.set_page_config(page_title="AI Governance & Evaluation Platform v0.6.0", layout="wide")




provider = StubProvider()
policy_engine = PolicyEngine(POLICY_PATH)
audit_logger = AuditLogger(LOG_PATH)
feedback_logger = FeedbackLogger(FEEDBACK_PATH)
feedback_gate = FeedbackGate(FEEDBACK_SUMMARY_PATH)
from ai_governance_platform.extraction.validation import (
    validate_loan_application, validate_disclosure, validate_credit_report, validate_appraisal_report,
    validate_income_verification, validate_bank_statement, validate_tax_return, validate_closing_documents
)
def parse_fields(text, doc_type):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    fields = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            fields[key.strip()] = value.strip()
    return fields

def build_object(doc_type, fields):
    if doc_type == 'Loan Application':
        return LoanApplication(
            fields.get('Applicant Name',''), fields.get('Property Address',''), fields.get('Loan Amount',''),
            fields.get('Interest Rate',''), fields.get('Term (years)',''), fields.get('Signature',''))
    elif doc_type == 'Disclosure':
        return Disclosure(
            fields.get('Disclosure Date',''), fields.get('Loan Terms',''), fields.get('Interest Rate',''),
            fields.get('Fees',''), fields.get('Signature',''))
    elif doc_type == 'Credit Report':
        return CreditReport(
            fields.get('Applicant Name',''), fields.get('Credit Score',''), fields.get('Report Date',''),
            fields.get('Accounts',''), fields.get('Signature',''))
    elif doc_type == 'Appraisal Report':
        return AppraisalReport(
            fields.get('Property Address',''), fields.get('Appraised Value',''), fields.get('Appraiser Name',''),
            fields.get('Date',''), fields.get('Signature',''))
    elif doc_type == 'Income Verification':
        return IncomeVerification(
            fields.get('Applicant Name',''), fields.get('Employer',''), fields.get('Income',''),
            fields.get('Tax Year',''), fields.get('Signature',''))
    elif doc_type == 'Bank Statement':
        return BankStatement(
            fields.get('Account Holder',''), fields.get('Account Number',''), fields.get('Balance',''),
            fields.get('Statement Date',''), fields.get('Signature',''))
    elif doc_type == 'Tax Return':
        return TaxReturn(
            fields.get('Taxpayer Name',''), fields.get('Year',''), fields.get('Income',''),
            fields.get('Deductions',''), fields.get('Signature',''))
    elif doc_type == 'Closing Documents':
        return ClosingDocuments(
            fields.get('Closing Date',''), fields.get('Property Address',''), fields.get('Loan Amount',''),
            fields.get('Buyer',''), fields.get('Seller',''), fields.get('Signature',''))
    else:
        return fields
from ai_governance_platform.extraction.document_types import (
LoanApplication, Disclosure, CreditReport, AppraisalReport, IncomeVerification, BankStatement, TaxReturn, ClosingDocuments
    )
st.header("Document Extraction & Review")
st.write("Upload a .zip file containing only PDFs, or an individual .pdf file.")

import zipfile
from io import BytesIO
import pdfplumber
import pandas as pd

uploaded_file = st.file_uploader(
    "Upload .zip or .pdf",
    type=["zip", "pdf"],
    key="file_upload"
)

pdf_contents = {}
pdf_files_bytes = {}
error_msg = None

def extract_pdf_text(pdf_bytes, pdf_name):
        def parse_fields(text, doc_type):
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            fields = {}
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    fields[key.strip()] = value.strip()
            return fields

        def build_object(doc_type, fields):
            if doc_type == 'Loan Application':
                return LoanApplication(
                    fields.get('Applicant Name',''), fields.get('Property Address',''), fields.get('Loan Amount',''),
                    fields.get('Interest Rate',''), fields.get('Term (years)',''), fields.get('Signature',''))
            elif doc_type == 'Disclosure':
                return Disclosure(
                    fields.get('Disclosure Date',''), fields.get('Loan Terms',''), fields.get('Interest Rate',''),
                    fields.get('Fees',''), fields.get('Signature',''))
            elif doc_type == 'Credit Report':
                return CreditReport(
                    fields.get('Applicant Name',''), fields.get('Credit Score',''), fields.get('Report Date',''),
                    fields.get('Accounts',''), fields.get('Signature',''))
            elif doc_type == 'Appraisal Report':
                return AppraisalReport(
                    fields.get('Property Address',''), fields.get('Appraised Value',''), fields.get('Appraiser Name',''),
                    fields.get('Date',''), fields.get('Signature',''))
            elif doc_type == 'Income Verification':
                return IncomeVerification(
                    fields.get('Applicant Name',''), fields.get('Employer',''), fields.get('Income',''),
                    fields.get('Tax Year',''), fields.get('Signature',''))
            elif doc_type == 'Bank Statement':
                return BankStatement(
                    fields.get('Account Holder',''), fields.get('Account Number',''), fields.get('Balance',''),
                    fields.get('Statement Date',''), fields.get('Signature',''))
            elif doc_type == 'Tax Return':
                return TaxReturn(
                    fields.get('Taxpayer Name',''), fields.get('Year',''), fields.get('Income',''),
                    fields.get('Deductions',''), fields.get('Signature',''))
            elif doc_type == 'Closing Documents':
                return ClosingDocuments(
                    fields.get('Closing Date',''), fields.get('Property Address',''), fields.get('Loan Amount',''),
                    fields.get('Buyer',''), fields.get('Seller',''), fields.get('Signature',''))
            else:
                return fields
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            return text

if uploaded_file:
    filename = uploaded_file.name.lower()
    if filename.endswith(".pdf"):
        pdf_bytes = uploaded_file.read()
        pdf_contents[filename] = extract_pdf_text(pdf_bytes, filename)
        pdf_files_bytes[filename] = pdf_bytes
    elif filename.endswith(".zip"):
        try:
            zip_bytes = BytesIO(uploaded_file.read())
            with zipfile.ZipFile(zip_bytes) as z:
                pdf_files = [f for f in z.namelist() if f.lower().endswith(".pdf")]
                non_pdf_files = [f for f in z.namelist() if not f.lower().endswith(".pdf")]
                if non_pdf_files:
                    error_msg = f"Error: .zip contains non-PDF files: {', '.join(non_pdf_files)}"
                else:
                    for pdf_file in pdf_files:
                        with z.open(pdf_file) as pdf_f:
                            pdf_bytes = pdf_f.read()
                            pdf_contents[pdf_file] = extract_pdf_text(pdf_bytes, pdf_file)
                            pdf_files_bytes[pdf_file] = pdf_bytes
        except zipfile.BadZipFile:
            error_msg = "Error: Invalid .zip file."
    else:
        error_msg = "Error: Unsupported file type."

if error_msg:
    st.error(error_msg)
elif pdf_contents:
    st.success(f"Extracted {len(pdf_contents)} PDF(s). Displaying extracted data:")
    def doc_type_from_name(name):
        return name.replace(".pdf","").replace("_"," ").title()
    data = []
    objects = []
    validation_results = []
    confidence_scores = []
    pdf_metadata = []
    for idx, (pdf_name, text) in enumerate(pdf_contents.items(), 1):
        doc_type = doc_type_from_name(pdf_name)
        fields = parse_fields(text, doc_type)
        obj = build_object(doc_type, fields)
        data.append({"Document #": idx, "Document Type": doc_type, "PDF Name": pdf_name, "Extracted Text": text})
        objects.append((doc_type, obj))
        # Store PDF metadata for later download/view
        pdf_bytes = None
        if pdf_name in pdf_files_bytes:
            pdf_bytes = pdf_files_bytes[pdf_name]
        pdf_metadata.append((idx, doc_type, pdf_name, pdf_bytes))
        # Validation
        if doc_type == 'Loan Application':
            errors = validate_loan_application(obj)
        elif doc_type == 'Disclosure':
            errors = validate_disclosure(obj)
        elif doc_type == 'Credit Report':
            errors = validate_credit_report(obj)
        elif doc_type == 'Appraisal Report':
            errors = validate_appraisal_report(obj)
        elif doc_type == 'Income Verification':
            errors = validate_income_verification(obj)
        elif doc_type == 'Bank Statement':
            errors = validate_bank_statement(obj)
        elif doc_type == 'Tax Return':
            errors = validate_tax_return(obj)
        elif doc_type == 'Closing Documents':
            errors = validate_closing_documents(obj)
        else:
            errors = []
        validation_results.append({"doc_type": doc_type, "errors": errors})
        # Confidence scoring
        def score_confidence(fields):
            score = 100
            # Penalize missing fields
            for k, v in fields.items():
                if not v or v.strip() == "":
                    score -= 10
            # Penalize short names
            if "Applicant Name" in fields and len(fields["Applicant Name"]) < 3:
                score -= 15
            # Penalize weird date formats
            for k in fields:
                if "Date" in k:
                    import re
                    if not re.match(r"\d{4}-\d{2}-\d{2}", fields[k]):
                        score -= 10
            # Penalize suspicious values
            if "Loan Amount" in fields and fields["Loan Amount"] in ["0", "", None]:
                score -= 20
            return max(score, 0)
        confidence_scores.append(score_confidence(fields))
    df = pd.DataFrame(data)
    df = df.sort_values("Document Type")
    st.session_state["pdf_metadata"] = pdf_metadata

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Document Extraction & Review", "Extracted Objects & Fields", "Confidence Scoring", "Escalation Required", "Audit Log"])
    with tab5:
        import csv, os
        audit_log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../logs/human_review_log.csv'))
        st.header("Audit Log: Loan Review Status")
        audit_entries = []
        if os.path.exists(audit_log_path):
            with open(audit_log_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    audit_entries.append(row)
        # Build summary for each loan
        loan_status = {}
        loan_status = {}
        reviewed_docs = st.session_state.get("reviewed_docs", set())
        loan_number = loan_numbers[0] if 'loan_numbers' in locals() and loan_numbers else 1
        for idx, (doc_type, obj) in enumerate(st.session_state.get("extracted_objects", [])):
            loan_num = loan_number
            score = confidence_scores[idx] if idx < len(confidence_scores) else None
            validation_errors = st.session_state["validation_results"][idx]["errors"] if st.session_state.get("validation_results") else []
            status = "Auto-approved"
            reviewer = ""
            action = ""
            reasons = ""
            pdf_name = ""
            for entry in audit_entries:
                if str(entry.get("loan_number")) == str(loan_num) and entry.get("doc_type") == doc_type:
                    reviewer = entry.get("reviewer", "")
                    action = entry.get("action", "")
                    reasons = entry.get("reasons", "")
                    pdf_name = entry.get("pdf_name", "")
                    if action == "Approve":
                        status = "Human-approved"
                    elif action == "Deny":
                        status = "Human-denied"
                    elif action == "Skip":
                        status = "Escalation Skipped"
            # Only mark as 'Human-approved' if it was escalated and reviewed
            if status == "Auto-approved" and ((score is not None and score < 90) or validation_errors):
                # If all escalated docs for this loan are reviewed, show in audit log
                escalated_docs = [(loan_num, dt) for dt, _ in st.session_state.get("extracted_objects", []) if ((score is not None and score < 90) or validation_errors)]
                if all(doc in reviewed_docs for doc in escalated_docs):
                    status = "Human-approved"
                else:
                    status = "Escalation Required"
            loan_status[idx] = {
                "Loan #": loan_num,
                "Document Type": doc_type,
                "Confidence Score": score,
                "Status": status,
                "Reviewer": reviewer,
                "Reasons": reasons,
                "PDF Name": pdf_name
            }
        # Display audit log table
        st.write("Below is the audit log for all loans:")
        st.dataframe(
            [v for v in loan_status.values()],
            use_container_width=True
        )

    with tab1:
        st.dataframe(df)
        if st.button("Extract Objects & Show Fields"):
            st.session_state["show_extraction_results"] = True
            st.session_state["extracted_objects"] = objects
            st.session_state["validation_results"] = validation_results
            st.session_state["extraction_summary"] = "All data valid." if all(len(r["errors"]) == 0 for r in validation_results) else "Validation errors found."
            st.info("Switch to the 'Extracted Objects & Fields' tab to view detailed results.")

    with tab2:
        if st.session_state.get("show_extraction_results"):
            all_errors = []
            for idx, result in enumerate(st.session_state["validation_results"]):
                if result["errors"]:
                    all_errors.append(f"{st.session_state['extracted_objects'][idx][0]}: {result['errors']}")
            if not all_errors:
                st.success("🟢 Extraction Summary: All data valid.")
            else:
                error_details = '\n'.join([f"- {err}" for err in all_errors])
                st.error(f"🔴 Extraction Summary: Validation errors found.\n\n**Details:**\n{error_details}")
            with st.expander("Object Details", expanded=False):
                for idx, (doc_type, obj) in enumerate(st.session_state["extracted_objects"]):
                    st.write(f"### {doc_type}")
                    st.json(obj.__dict__)
                    errors = st.session_state["validation_results"][idx]["errors"]
                    score = confidence_scores[idx] if idx < len(confidence_scores) else None
                    if errors:
                        st.warning(f"Validation errors: {errors}")
                    else:
                        st.success("All fields valid.")
                    # Confidence score not shown in this tab

    with tab3:
        if st.session_state.get("show_extraction_results"):
            st.write("## Confidence Scoring Results")
            for idx, (doc_type, obj) in enumerate(st.session_state["extracted_objects"]):
                score = confidence_scores[idx] if idx < len(confidence_scores) else None
                reasons = []
                fields = obj.__dict__ if hasattr(obj, '__dict__') else obj
                # Re-run confidence scoring logic for reasons
                reasons = []
                if score is not None and score < 100:
                    for k, v in fields.items():
                        if not v or v.strip() == "":
                            reasons.append(f"{k} missing")
                    if "Applicant Name" in fields and len(fields["Applicant Name"]) < 3:
                        reasons.append("Applicant Name too short")
                    for k in fields:
                        if "Date" in k:
                            import re
                            if not re.match(r"\d{4}-\d{2}-\d{2}", fields[k]):
                                reasons.append(f"{k} format invalid")
                    if "Loan Amount" in fields and fields["Loan Amount"] in ["0", "", None]:
                        reasons.append("Loan Amount not positive")
                if score is not None:
                    if score == 100:
                        st.success(f"{doc_type}: Confidence Score {score}/100 (Perfect)")
                    elif score >= 90:
                        st.warning(f"{doc_type}: Confidence Score {score}/100")
                        if reasons:
                            st.write("**Reasons for minor issues:**")
                            for r in reasons:
                                st.write(f"- {r}")
                    else:
                        st.error(f"{doc_type}: Confidence Score {score}/100")
                        if reasons:
                            st.write("**Reasons for major issues:**")
                            for r in reasons:
                                st.write(f"- {r}")
    with tab4:
        if st.session_state.get("show_extraction_results"):
            import csv, os, datetime
            audit_log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../logs/human_review_log.csv'))
            escalated = []
            # Assign the next available loan number by checking audit log
            import csv
            audit_log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../logs/human_review_log.csv'))
            max_loan_number = 0
            if os.path.exists(audit_log_path):
                with open(audit_log_path, mode="r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            num = int(row.get("loan_number", 0))
                            if num > max_loan_number:
                                max_loan_number = num
                        except Exception:
                            pass
            loan_number = max_loan_number + 1
            loan_numbers = [loan_number] * len(st.session_state["extracted_objects"])
            pdf_metadata = st.session_state.get("pdf_metadata", [])
            reviewed_docs = st.session_state.get("reviewed_docs", set())
            for idx, (doc_type, obj) in enumerate(st.session_state["extracted_objects"]):
                score = confidence_scores[idx] if idx < len(confidence_scores) else None
                reasons = []
                fields = obj.__dict__ if hasattr(obj, '__dict__') else obj
                # Re-run confidence scoring logic for reasons
                reasons = []
                loan_num = loan_numbers[idx]
                validation_errors = st.session_state["validation_results"][idx]["errors"] if st.session_state.get("validation_results") else []
                validation_errors = st.session_state["validation_results"][idx]["errors"] if st.session_state.get("validation_results") else []
                if ((score is not None and score < 90) or validation_errors) and (loan_num, doc_type) not in reviewed_docs:
                    for k, v in fields.items():
                        if not v or v.strip() == "":
                            reasons.append(f"{k} missing")
                    if "Applicant Name" in fields and len(fields["Applicant Name"]) < 3:
                        reasons.append("Applicant Name too short")
                    for k in fields:
                        if "Date" in k:
                            import re
                            if not re.match(r"\d{4}-\d{2}-\d{2}", fields[k]):
                                reasons.append(f"{k} format invalid")
                    if "Loan Amount" in fields and fields["Loan Amount"] in ["0", "", None]:
                        reasons.append("Loan Amount not positive")
                    # Add validation errors to escalation reasons
                    if validation_errors:
                        reasons.extend([f"Validation error ({doc_type}): {err}" for err in validation_errors])
                    # Find PDF bytes for this loan
                    pdf_bytes = None
                    pdf_name = None
                    for meta in pdf_metadata:
                        if meta[0] == idx+1 and meta[2]:
                            pdf_name = meta[2]
                            pdf_bytes = meta[3]
                            break
                    escalated.append((idx, doc_type, obj, score, reasons, loan_num, pdf_name, pdf_bytes))
            if escalated:
                st.error("⚠️ Escalation Required: The following objects require human review due to low confidence.")
                reviewer = st.text_input("Reviewer Name", value="")
                for idx, doc_type, obj, score, reasons, loan_num, pdf_name, pdf_bytes in escalated:
                    with st.expander(f"Escalation: Loan #{loan_num} - {doc_type} (Score: {score}/100)", expanded=False):
                        st.write(f"### Reasons for escalation ({doc_type}):")
                        for r in reasons:
                            st.write(f"- {r}")
                        st.write("---")
                        st.write(f"### Object and variable view ({doc_type}):")
                        st.json(obj.__dict__)
                        st.write("---")
                        if pdf_bytes:
                            st.download_button(
                                label=f"Download PDF for {doc_type}",
                                data=pdf_bytes,
                                file_name=pdf_name or f"{doc_type.replace(' ', '_')}.pdf",
                                mime="application/pdf"
                            )
                        st.write("---")
                        action = st.radio(f"Human Review Action for {doc_type}", ["Approve", "Deny", "Skip"], key=f"escalate_action_{idx}")
                        if st.button(f"Submit Review for {doc_type}", key=f"submit_escalate_{idx}"):
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            log_entry = [timestamp, reviewer, loan_num, doc_type, action, score, ", ".join(reasons), pdf_name]
                            header = ["timestamp", "reviewer", "loan_number", "doc_type", "action", "confidence_score", "reasons", "pdf_name"]
                            file_exists = os.path.exists(audit_log_path)
                            with open(audit_log_path, mode="a", newline="", encoding="utf-8") as f:
                                writer = csv.writer(f)
                                if not file_exists or os.stat(audit_log_path).st_size == 0:
                                    writer.writerow(header)
                                writer.writerow(log_entry)
                            # Mark document as reviewed
                            if "reviewed_docs" not in st.session_state:
                                st.session_state["reviewed_docs"] = set()
                            st.session_state["reviewed_docs"].add((loan_num, doc_type))
                            st.success(f"Action '{action}' recorded for {doc_type} and logged. This document will now be removed from the escalation list.")
                            st.rerun()
        else:
            st.info("No extraction results yet. Run extraction in the first tab.")
            from ai_governance_platform.escalation.escalation import load_pending_escalations
            pending_escalations = load_pending_escalations()
            escalation_indices = list(pending_escalations.index)
            current_idx = st.session_state.get('escalation_idx', escalation_indices[0] if escalation_indices else 0)
            # Show only the current escalation

    # Always show info message if no query context is present
    if st.session_state.get("show_feedback_info", False):
        st.info("Feedback submitted successfully! Enter a prompt and click 'Run Query' to get started.")
        st.session_state["show_feedback_info"] = False
    elif "last_query_context" not in st.session_state:
    # Show last query result if available
        if "last_query_context" in st.session_state:
            context = st.session_state["last_query_context"]
            response = st.session_state["last_query_response"]
            decision = st.session_state["last_query_decision"]
            # ...existing code...
            st.write(f"**Query:** {context['prompt']}")
            st.write(f"**Decision:** {decision['decision']}")
            st.write(f"**Risk Level:** {decision['risk_level']}")
            st.write(f"**Rule Triggered:** {decision.get('rule_triggered') or 'No rule triggered'}")
            st.write(f"**Reason:** {decision.get('reason') or 'No reason'}")
            st.write(f"**Response:** {response if response else '[No response generated]'}")

            # Show escalation warning and human action if needed
            if decision['decision'] == 'escalate':
                st.warning("⚠️ This query has been escalated and requires human review or intervention. Please assign a responsible person to handle this escalation.")
                st.info("Escalation actions may include: reviewing the query, approving or denying access, or following up with compliance/audit teams.")

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
                    for key in ["last_query_context", "last_query_response", "last_query_decision", "last_prompt", "last_response"]:
                        if key in st.session_state:
                            del st.session_state[key]
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