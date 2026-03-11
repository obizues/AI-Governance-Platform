from ai_governance_platform.services.validation_service import (
    validate_loan_application, validate_disclosure, validate_credit_report, validate_appraisal_report,
    validate_income_verification, validate_bank_statement, validate_tax_return, validate_closing_documents
)
from ai_governance_platform.services.provider_service import ProviderService
from ai_governance_platform.services.escalation_service import EscalationService
from ai_governance_platform.services.metrics_service import MetricsService
import os
import json
import sys
from ai_governance_platform.services.audit_logging_service import AuditLoggingService
from ai_governance_platform.services.feedback_service import FeedbackService
from ai_governance_platform.services.policy_service import PolicyService
from ai_governance_platform.services.evaluation_service import EvaluationService
import yaml
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "logs"))
LOG_FILE = "ai_interactions.csv"
FEEDBACK_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "logs"))
FEEDBACK_FILE = "feedback_log.csv"
FEEDBACK_SUMMARY_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "logs", "feedback_summary.json"))
POLICY_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "policy", "policy.yaml"))

__all__ = ["main"]

def main():
    confidence_scores = []
    try:
        # All Streamlit UI logic below
        import os
        import json
        import sys
        from ai_governance_platform.services.audit_logging_service import AuditLoggingService
        from ai_governance_platform.services.feedback_service import FeedbackService
        from ai_governance_platform.services.policy_service import PolicyService
        from ai_governance_platform.services.evaluation_service import EvaluationService
        import yaml
        import streamlit as st

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        LOG_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "logs"))
        LOG_FILE = "ai_interactions.csv"
        FEEDBACK_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "logs"))
        FEEDBACK_FILE = "feedback_log.csv"
        FEEDBACK_SUMMARY_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "logs", "feedback_summary.json"))
        POLICY_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "policy", "policy.yaml"))
        
        # Ensure log files exist and are initialized for Streamlit Cloud
        log_files = [
            os.path.join(LOG_DIR, LOG_FILE),
            os.path.abspath(os.path.join(BASE_DIR, "..", "..", "logs", "hil_actions.csv"))
        ]
        for lf in log_files:
            from ai_governance_platform.services.file_management_service import FileManagementService
            file_service = FileManagementService(base_dir=FEEDBACK_DIR)
            if not os.path.exists(lf):
                if "ai_interactions.csv" in lf:
                    file_service.write_csv(os.path.basename(lf), [{"timestamp": "", "loan_id": "", "action": "", "details": ""}])
                elif "hil_actions.csv" in lf:
                    file_service.write_csv(os.path.basename(lf), [{"timestamp": "", "loan_id": "", "reviewer": "", "action": "", "notes": ""}])

        # Render banners only once at the top
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
        st.set_page_config(page_title="AI Governance & Evaluation Platform v0.8.1", layout="wide")
        from ai_governance_platform.services.provider_service import StubProvider, ProviderService
        stub = StubProvider()
        provider_service = ProviderService(provider=stub)
        provider = provider_service.provider
        policy_service = PolicyService(policy_path=POLICY_PATH)
        audit_logger = AuditLoggingService(log_dir=LOG_DIR, log_file=LOG_FILE)
        # ...existing Streamlit UI logic (file upload, extraction, tabs, etc.)...
        # After loan_id and pdf_name are assigned:
        # Define loan_id and pdf_name if available
        loan_id = st.session_state.get("current_loan_number")
        # Use st.session_state to retrieve uploaded file name if available
        pdf_name = st.session_state.get("uploaded_file_name")
        if loan_id is not None and pdf_name is not None:
            audit_logger.log_event(
                event_type="extraction",
                user="system",
                details={"loan_id": loan_id, "pdf_name": pdf_name, "status": "extracted"}
            )
        feedback_logger = FeedbackService(log_dir=FEEDBACK_DIR, log_file=FEEDBACK_FILE)
        from ai_governance_platform.services.feedback_service import FeedbackService
        feedback_gate = FeedbackService(log_dir=os.path.dirname(FEEDBACK_SUMMARY_PATH), log_file=os.path.basename(FEEDBACK_SUMMARY_PATH))
        # Remove incorrect import or ensure correct function signature
        # from ai_governance_platform.services.extraction_service import extract_pdf_text
        # Removed local import for validate_loan_application
        # ...existing Streamlit UI logic (file upload, extraction, tabs, etc.)...
    # tab3_container block moved inside try block below
        if st.session_state.get("show_extraction_results"):
            st.write("## Confidence Scoring Results")
            for idx, (doc_type, obj) in enumerate(st.session_state["extracted_objects"]):
                score = confidence_scores[idx] if idx < len(confidence_scores) else None
                fields = obj.__dict__ if hasattr(obj, '__dict__') else obj
                reasons = []
                if score is not None:
                    for k, v in fields.items():
                        if not v or v.strip() == "":
                            reasons.append(f"{k} missing")
                    if "applicant_name" in fields and len(fields["applicant_name"]) < 3 and fields["applicant_name"].strip() != "":
                        reasons.append("Applicant name too short")
                    for k in fields:
                        if "date" in k:
                            import re
                            if fields[k].strip() != "" and not re.match(r"\d{4}-\d{2}-\d{2}", fields[k]):
                                reasons.append(f"{k} format invalid")
                    if "loan_amount" in fields and fields["loan_amount"] in ["0", "", None]:
                        reasons.append("Loan amount not positive")
                    if score == 100:
                        st.success(f"**{doc_type}: Confidence Score {score}/100 (Perfect)**")
                    elif score >= 90:
                        st.warning(f"**{doc_type}: Confidence Score {score}/100**")
                        if reasons:
                            st.markdown("<span style='color:#666;font-weight:bold;'>Reasons for minor issues:</span>", unsafe_allow_html=True)
                            st.markdown("\n".join([f"- {r}" for r in reasons]))
                    else:
                        st.error(f"**{doc_type}: Confidence Score {score}/100**")
                        if reasons:
                            st.markdown("<span style='color:#b00;font-weight:bold;'>Reasons for major issues:</span>", unsafe_allow_html=True)
                            st.markdown("\n".join([f"- {r}" for r in reasons]))
        # tab4_container block moved inside try block below
            if st.session_state.get("show_extraction_results"):
                import csv, os, datetime
                audit_log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../logs/human_review_log.csv'))
                escalated = []
                loan_escalations = {}
                # Assign the next available loan number by checking audit log
                import csv
                audit_log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../logs/human_review_log.csv'))
                max_loan_number = 0
                from ai_governance_platform.services.file_management_service import FileManagementService
                file_service = FileManagementService(base_dir=os.path.dirname(audit_log_path))
                audit_log_rows = file_service.read_csv(os.path.basename(audit_log_path))
                reader = audit_log_rows
                for row in reader:
                    try:
                        num = int(row.get("loan_number", 0))
                        if num > max_loan_number:
                            max_loan_number = num
                    except Exception:
                        pass
                # Only increment loan number for new uploads, not for each review
                if "current_loan_number" not in st.session_state:
                    st.session_state["current_loan_number"] = max_loan_number + 1
                loan_number = st.session_state["current_loan_number"]
                loan_numbers = [loan_number] * len(st.session_state["extracted_objects"])
                pdf_metadata = st.session_state.get("pdf_metadata", [])
                reviewed_docs = st.session_state.get("reviewed_docs", set())
                for idx, (doc_type, obj) in enumerate(st.session_state["extracted_objects"]):
                    score = confidence_scores[idx] if idx < len(confidence_scores) else None
                    reasons = []
                    fields = obj.__dict__ if hasattr(obj, '__dict__') else obj
                    loan_num = loan_numbers[idx]
                    validation_errors = st.session_state["validation_results"][idx]["errors"] if st.session_state.get("validation_results") else []
                    if ((score is not None and score < 90) or validation_errors) and all((loan_num, doc['doc_type']) not in reviewed_docs for doc in loan_escalations.get(loan_num, [])):
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
                        if validation_errors:
                            reasons.extend([f"Validation error ({doc_type}): {err}" for err in validation_errors])
                        pdf_bytes = None
                        pdf_name = None
                        for meta in pdf_metadata:
                            if meta[0] == idx+1 and meta[2]:
                                pdf_name = meta[2]
                                pdf_bytes = meta[3]
                                break
                        # Group escalations by loan number
                        if loan_num not in loan_escalations:
                            loan_escalations[loan_num] = []
                        loan_escalations[loan_num].append({
                            "idx": idx,
                            "doc_type": doc_type,
                            "obj": obj,
                            "score": score,
                            "reasons": reasons,
                            "pdf_name": pdf_name,
                            "pdf_bytes": pdf_bytes
                        })
                reviewed_loans = set(loan_num for (loan_num, doc_type) in st.session_state.get("reviewed_docs", set()))
                visible_loans = [loan_num for loan_num in loan_escalations.keys() if loan_num not in reviewed_loans]
                if not visible_loans:
                    st.markdown("<div style='background-color:#e0e0e0;padding:10px;border-radius:5px;margin-bottom:10px'><b>No loans require escalation review at this time.</b></div>", unsafe_allow_html=True)
                else:
                    st.error("⚠️ Escalation Required: The following loans require human review due to low confidence or validation errors.")
                    reviewer = st.text_input("Reviewer Name", value="")
                    for loan_num in visible_loans:
                        docs = loan_escalations[loan_num]
                        with st.expander(f"Escalation: Loan #{loan_num} - {len(docs)} document(s)", expanded=False):
                            st.write("### Reasons for escalation:")
                            for doc in docs:
                                st.write(f"**{doc['doc_type']}**:")
                                # Deduplicate reasons and sort for clarity
                                # Only show validation function errors, no UI-generated missing field errors
                                validation_reasons = []
                                for reason in doc['reasons']:
                                    if reason.startswith("Validation error") and reason not in validation_reasons:
                                        validation_reasons.append(reason)
                                validation_reasons = sorted(set(validation_reasons))
                                st.markdown("<ul style='margin-left:1em;'>" + "".join([f"<li style='margin-bottom:4px;'>{r}</li>" for r in validation_reasons]) + "</ul>", unsafe_allow_html=True)
                            st.write("---")
                            st.write("### Object and variable views:")
                            for doc in docs:
                                st.write(f"**{doc['doc_type']}**:")
                                st.json(doc['obj'].__dict__)
                            st.write("---")
                            st.write("### Download PDFs:")
                            for doc in docs:
                                if doc['pdf_bytes']:
                                    st.download_button(
                                        label=f"Download PDF for {doc['doc_type']}",
                                        data=doc['pdf_bytes'],
                                        file_name=doc['pdf_name'] or f"{doc['doc_type'].replace(' ', '_')}.pdf",
                                        mime="application/pdf"
                                    )
                            st.write("---")
                            action = st.radio(f"Human Review Action for Loan #{loan_num}", ["Approve", "Deny", "Skip"], key=f"escalate_action_{loan_num}")
                            if st.button(f"Submit Review for Loan #{loan_num}", key=f"submit_escalate_{loan_num}"):
                                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                header = ["timestamp", "reviewer", "loan_number", "doc_type", "action", "confidence_score", "reasons", "pdf_name"]
                                from ai_governance_platform.services.file_management_service import FileManagementService
                                file_service = FileManagementService(base_dir=os.path.dirname(audit_log_path))
                                for doc in docs:
                                    log_entry = {
                                        "timestamp": timestamp,
                                        "reviewer": reviewer,
                                        "loan_num": loan_num,
                                        "doc_type": doc['doc_type'],
                                        "action": action,
                                        "score": doc['score'],
                                        "reasons": ", ".join(doc['reasons']),
                                        "pdf_name": doc['pdf_name']
                                    }
                                    file_service.append_csv(os.path.basename(audit_log_path), log_entry)
                                    # Mark document as reviewed
                                    if "reviewed_docs" not in st.session_state:
                                        st.session_state["reviewed_docs"] = set()
                                    st.session_state["reviewed_docs"].add((loan_num, doc['doc_type']))
                                st.success(f"Action '{action}' recorded for Loan #{loan_num} and logged. All documents for this loan will now be removed from the escalation list.")
                                st.rerun()
    except Exception as e:
        st.error(f"A fatal error occurred: {str(e)}")
        print(f"Streamlit fatal error: {str(e)}")

    st.sidebar.markdown("""
    <div style='background:#eaf6ff;border:1.5px solid #b3e5fc;padding:10px 12px 8px 12px;margin-bottom:12px;text-align:center;border-radius:8px;'>
        <span style='font-size:1.08em;font-weight:600;color:#1976d2;'>App version:</span><br>
        <span style='font-size:1.05em;color:#222;'>v0.9.0 - Demo Files Sidebar, Dynamic Listing, UI/UX Improvements, Audit Log, Real-time Sync, Human Review Workflow, Document Extraction & Validation</span>
    </div>
    <div class='sidebar-card' style='background:#eaf6ff;font-size:0.93em;margin-bottom:16px;border:1.5px solid #b3e5fc;padding:8px 8px 6px 8px;'>
        <div style='font-weight:700;font-size:1em;line-height:1.2;margin-bottom:2px;text-align:center;'>
            <span style="font-size:1.05em;vertical-align:middle;">🤖</span> AI Governance & Evaluation Platform v0.9.0
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

    # Demo Files expander in sidebar
    import glob
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
    """

    """

    st.set_page_config(page_title="AI Governance & Evaluation Platform v0.9.0", layout="wide")

    from ai_governance_platform.services.provider_service import StubProvider, ProviderService
    stub = StubProvider()
    provider_service = ProviderService(provider=stub)
    provider = provider_service.provider
    policy_service = PolicyService(policy_path=POLICY_PATH)
    audit_logger = AuditLoggingService(log_dir=LOG_DIR, log_file=LOG_FILE)
    # Example usage: log an audit event after loan validation
    # After loan_id and validation_result are assigned:
    # Define loan_id and validation_result if available
    loan_id = st.session_state.get("current_loan_number")
    validation_result = st.session_state.get("validation_results")
    if loan_id is not None and validation_result is not None:
        audit_logger.log_event(
            event_type="validation",
            user="system",
            details={"loan_id": loan_id, "validation_result": validation_result}
        )
    feedback_logger = FeedbackService(log_dir=FEEDBACK_DIR, log_file=FEEDBACK_FILE)
    from ai_governance_platform.services.feedback_service import FeedbackService
    feedback_gate = FeedbackService(log_dir=os.path.dirname(FEEDBACK_SUMMARY_PATH), log_file=os.path.basename(FEEDBACK_SUMMARY_PATH))
    import importlib
    import sys
    validation_imported = False
    try:
        # Removed invalid imports for extraction.validation
            validation_imported = True
    except ModuleNotFoundError:
        # Try adding extraction to sys.path and import directly
        import os
        extraction_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../extraction'))
        if extraction_path not in sys.path:
            sys.path.append(extraction_path)
        validation_module = importlib.import_module('validation')
        # Removed local assignments for validation functions
    def parse_fields(text, doc_type):
        import re
        def to_snake_case(s):
            s = s.replace('(', '').replace(')', '')
            s = re.sub(r'[^a-zA-Z0-9 ]', '', s)
            s = s.replace(' ', '_')
            return s.lower()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        fields = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                snake_key = to_snake_case(key.strip())
                fields[snake_key] = value.strip()
        return fields

    def build_object(doc_type, fields):
        if doc_type == 'Loan Application':
            return LoanApplication(
                fields.get('applicant_name',''), fields.get('property_address',''), fields.get('loan_amount',''),
                fields.get('interest_rate',''), fields.get('term_years',''), fields.get('signature',''))
        elif doc_type == 'Disclosure':
            return Disclosure(
                fields.get('disclosure_date',''), fields.get('loan_terms',''), fields.get('interest_rate',''),
                fields.get('fees',''), fields.get('signature',''))
        elif doc_type == 'Credit Report':
            return CreditReport(
                fields.get('applicant_name',''), fields.get('credit_score',''), fields.get('report_date',''),
                fields.get('accounts',''), fields.get('signature',''))
        elif doc_type == 'Appraisal Report':
            return AppraisalReport(
                fields.get('property_address',''), fields.get('appraised_value',''), fields.get('appraiser_name',''),
                fields.get('date',''), fields.get('signature',''))
        elif doc_type == 'Income Verification':
            return IncomeVerification(
                fields.get('applicant_name',''), fields.get('employer',''), fields.get('income',''),
                fields.get('tax_year',''), fields.get('signature',''))
        elif doc_type == 'Bank Statement':
            return BankStatement(
                fields.get('account_holder',''), fields.get('account_number',''), fields.get('balance',''),
                fields.get('statement_date',''), fields.get('signature',''))
        elif doc_type == 'Tax Return':
            return TaxReturn(
                fields.get('taxpayer_name',''), fields.get('year',''), fields.get('income',''),
                fields.get('deductions',''), fields.get('signature',''))
        elif doc_type == 'Closing Documents':
            return ClosingDocuments(
                fields.get('closing_date',''), fields.get('property_address',''), fields.get('loan_amount',''),
                fields.get('buyer',''), fields.get('seller',''), fields.get('signature',''))
        else:
            return fields
    from ai_governance_platform.models.document_types import (
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
                            try:
                                with z.open(pdf_file) as pdf_f:
                                    pdf_bytes = pdf_f.read()
                                    pdf_contents[pdf_file] = extract_pdf_text(pdf_bytes, pdf_file)
                                    pdf_files_bytes[pdf_file] = pdf_bytes
                            except Exception as e:
                                error_msg = f"Error extracting {pdf_file}: {str(e)}"
                                st.error(error_msg)
            except zipfile.BadZipFile:
                error_msg = "Error: Invalid .zip file."
            except Exception as e:
                error_msg = f"Unexpected error during zip extraction: {str(e)}"
                st.error(error_msg)
        else:
            error_msg = "Error: Unsupported file type."

    if error_msg:
        st.error(error_msg)
        print(f"Streamlit error: {error_msg}")
        # Instead of stopping, show error and continue rendering the rest of the app
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
            try:
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
                    missing = False
                    for k, v in fields.items():
                        if not v or v.strip() == "":
                            missing = True
                    # Other penalties (optional, but not for red)
                    if not missing:
                        if "applicant_name" in fields and len(fields["applicant_name"]) < 3:
                            score -= 15
                        for k in fields:
                            if "date" in k:
                                import re
                                if not re.match(r"\d{4}-\d{2}-\d{2}", fields[k]):
                                    score -= 10
                        if "loan_amount" in fields and fields["loan_amount"] in ["0", "", None]:
                            score -= 20
                    if missing:
                        score = 50  # Always red if any missing field
                    return max(score, 0)
                confidence_scores.append(score_confidence(fields))
            except Exception as e:
                st.error(f"Error processing {pdf_name}: {str(e)}")
                print(f"Streamlit error processing {pdf_name}: {str(e)}")
        df = pd.DataFrame(data)
        if "Document Type" in df.columns:
            df = df.sort_values("Document Type")
        else:
            st.warning("No 'Document Type' column found in extracted data. Sorting skipped.")
        st.session_state["pdf_metadata"] = pdf_metadata
        # Log KPIs: confidence scores and validation counts
        metrics_service = MetricsService(log_dir=os.path.join(BASE_DIR, '..', '..', 'logs'))
        for idx, score in enumerate(confidence_scores):
            metrics_service.log_kpi("confidence_score", score, {"doc_type": data[idx]["Document Type"], "pdf_name": data[idx]["PDF Name"]})
        metrics_service.log_kpi("validation_count", len(validation_results))

        try:
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Document Extraction & Review", "Extracted Objects & Fields", "Confidence Scoring", "Escalation Required", "Audit Log"])
            with tab5:
                audit_log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../logs/human_review_log.csv'))
                st.header("Audit Log: Loan Review Status")
                import pandas as pd
                from ai_governance_platform.services.file_management_service import FileManagementService
                file_service = FileManagementService(base_dir=os.path.dirname(audit_log_path))
                audit_log_rows = file_service.read_csv(os.path.basename(audit_log_path))
                import pandas as pd
                df_audit = pd.DataFrame(audit_log_rows)
                # Ensure all expected columns exist
                expected_cols = [
                    "timestamp", "user_role", "prompt", "response", "response_time_ms",
                    "confidence_score", "risk_level", "decision", "rule_triggered", "reason",
                    "required_controls", "hil_action", "hil_reviewer"
                ]
                for col in expected_cols:
                    if col not in df_audit.columns:
                        df_audit[col] = ''
                if not df_audit.empty:
                    st.write("Below is the audit log for all loans:")
                    # Only show columns up to and including pdf_name
                    if 'pdf_name' in df_audit.columns:
                        pdf_idx = df_audit.columns.get_loc('pdf_name')
                        if isinstance(pdf_idx, int):
                            col_list = list(df_audit.columns)
                            cols_to_show = col_list[:pdf_idx+1]
                            st.dataframe(df_audit[cols_to_show], width='stretch')
                        else:
                            st.dataframe(df_audit, width='stretch')
                    else:
                        st.dataframe(df_audit, width='stretch')
                else:
                    st.info("No audit log entries found.")
        except Exception as e:
            st.error(f"Error rendering tabs: {str(e)}")
            print(f"Streamlit error: {str(e)}")

        tab1_container = tab1
        with tab1_container:
            st.dataframe(df)
            # Automatically extract and show results when upload completes
            st.session_state["show_extraction_results"] = True
            st.session_state["extracted_objects"] = objects
            st.session_state["validation_results"] = validation_results
            st.session_state["extraction_summary"] = "All data valid." if all(len(r["errors"]) == 0 for r in validation_results) else "Validation errors found."
            try:
                st.info("Extraction completed automatically. Switch to the 'Extracted Objects & Fields' tab to view detailed results.")
            except Exception as e:
                st.error(f"Error displaying extraction info: {str(e)}")
                print(f"Streamlit error: {str(e)}")

        tab2_container = tab2
        with tab2_container:
            if st.session_state.get("show_extraction_results"):
                try:
                    # Show extraction summary string
                    summary = st.session_state.get("extraction_summary", "No summary available.")
                    if "All data valid" in summary:
                        st.success(f"🟢 Extraction Summary: {summary}")
                    else:
                        st.error(f"🔴 Extraction Summary: {summary}")
                    # Show detailed errors
                    all_errors = []
                    for idx, result in enumerate(st.session_state["validation_results"]):
                        if result["errors"]:
                            all_errors.append(f"{st.session_state['extracted_objects'][idx][0]}: {result['errors']}")
                    if all_errors:
                        error_details = '\n'.join([f"- {err}" for err in all_errors])
                        st.markdown(f"**Details:**\n{error_details}")
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
                except Exception as e:
                    st.error(f"Error displaying extraction results: {str(e)}")
                    print(f"Streamlit error: {str(e)}")

        tab3_container = tab3
        with tab3_container:
            if st.session_state.get("show_extraction_results"):
                st.write("## Confidence Scoring Results")
                for idx, (doc_type, obj) in enumerate(st.session_state["extracted_objects"]):
                    score = confidence_scores[idx] if idx < len(confidence_scores) else None
                    fields = obj.__dict__ if hasattr(obj, '__dict__') else obj
                    reasons = []
                    if score is not None:
                        for k, v in fields.items():
                            if not v or v.strip() == "":
                                reasons.append(f"{k} missing")
                        if "applicant_name" in fields and len(fields["applicant_name"]) < 3 and fields["applicant_name"].strip() != "":
                            reasons.append("Applicant name too short")
                        for k in fields:
                            if "date" in k:
                                import re
                                if fields[k].strip() != "" and not re.match(r"\d{4}-\d{2}-\d{2}", fields[k]):
                                    reasons.append(f"{k} format invalid")
                        if "loan_amount" in fields and fields["loan_amount"] in ["0", "", None]:
                            reasons.append("Loan amount not positive")
                        if score == 100:
                            st.success(f"**{doc_type}: Confidence Score {score}/100 (Perfect)**")
                        elif score >= 90:
                            st.warning(f"**{doc_type}: Confidence Score {score}/100**")
                            if reasons:
                                st.markdown("<span style='color:#666;font-weight:bold;'>Reasons for minor issues:</span>", unsafe_allow_html=True)
                                st.markdown("\n".join([f"- {r}" for r in reasons]))
                        else:
                            st.error(f"**{doc_type}: Confidence Score {score}/100**")
                            if reasons:
                                st.markdown("<span style='color:#b00;font-weight:bold;'>Reasons for major issues:</span>", unsafe_allow_html=True)
                                st.markdown("\n".join([f"- {r}" for r in reasons]))
        tab4_container = tab4
        with tab4_container:
            if st.session_state.get("show_extraction_results"):
                import csv, os, datetime
                audit_log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../logs/human_review_log.csv'))
                escalated = []
                loan_escalations = {}
            # Assign the next available loan number by checking audit log
            import csv
            audit_log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../logs/human_review_log.csv'))
            max_loan_number = 0
            from ai_governance_platform.services.file_management_service import FileManagementService
            file_service = FileManagementService(base_dir=os.path.dirname(audit_log_path))
            audit_log_rows = file_service.read_csv(os.path.basename(audit_log_path))
            reader = audit_log_rows
            for row in reader:
                try:
                    num = int(row.get("loan_number", 0))
                    if num > max_loan_number:
                        max_loan_number = num
                except Exception:
                    pass
            # Only increment loan number for new uploads, not for each review
            if "current_loan_number" not in st.session_state:
                st.session_state["current_loan_number"] = max_loan_number + 1
            loan_number = st.session_state["current_loan_number"]
            loan_numbers = [loan_number] * len(st.session_state["extracted_objects"])
            pdf_metadata = st.session_state.get("pdf_metadata", [])
            reviewed_docs = st.session_state.get("reviewed_docs", set())
            for idx, (doc_type, obj) in enumerate(st.session_state["extracted_objects"]):
                score = confidence_scores[idx] if idx < len(confidence_scores) else None
                reasons = []
                fields = obj.__dict__ if hasattr(obj, '__dict__') else obj
                loan_num = loan_numbers[idx]
                if st.session_state.get("validation_results") and idx < len(st.session_state["validation_results"]):
                    validation_errors = st.session_state["validation_results"][idx]["errors"]
                else:
                    validation_errors = []
                if ((score is not None and score < 90) or validation_errors) and all((loan_num, doc['doc_type']) not in reviewed_docs for doc in loan_escalations.get(loan_num, [])):
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
                    if validation_errors:
                        reasons.extend([f"Validation error ({doc_type}): {err}" for err in validation_errors])
                    pdf_bytes = None
                    pdf_name = None
                    for meta in pdf_metadata:
                        if meta[0] == idx+1 and meta[2]:
                            pdf_name = meta[2]
                            pdf_bytes = meta[3]
                            break
                    # Group escalations by loan number
                    if loan_num not in loan_escalations:
                        loan_escalations[loan_num] = []
                    loan_escalations[loan_num].append({
                        "idx": idx,
                        "doc_type": doc_type,
                        "obj": obj,
                        "score": score,
                        "reasons": reasons,
                        "pdf_name": pdf_name,
                        "pdf_bytes": pdf_bytes
                    })
            reviewed_loans = set(loan_num for (loan_num, doc_type) in st.session_state.get("reviewed_docs", set()))
            visible_loans = [loan_num for loan_num in loan_escalations.keys() if loan_num not in reviewed_loans]
            if not visible_loans:
                st.markdown("<div style='background-color:#e0e0e0;padding:10px;border-radius:5px;margin-bottom:10px'><b>No loans require escalation review at this time.</b></div>", unsafe_allow_html=True)
            else:
                st.error("⚠️ Escalation Required: The following loans require human review due to low confidence or validation errors.")
                reviewer = st.text_input("Reviewer Name", value="")
                for loan_num in visible_loans:
                    docs = loan_escalations[loan_num]
                    with st.expander(f"Escalation: Loan #{loan_num} - {len(docs)} document(s)", expanded=False):
                        st.write("### Reasons for escalation:")
                        for doc in docs:
                            st.write(f"**{doc['doc_type']}**:")
                            # Deduplicate reasons and sort for clarity
                            # Only show missing fields as data validation errors
                            doc_fields = doc['obj'].__dict__ if hasattr(doc['obj'], '__dict__') else doc['obj']
                            validation_reasons = []
                            for field, value in doc_fields.items():
                                if value == "":
                            # Only show validation function errors, no UI-generated missing field errors
                                    validation_reasons = []
                            for reason in doc['reasons']:
                                if reason.startswith("Validation error") and reason not in validation_reasons:
                                    validation_reasons.append(reason)
                            validation_reasons = sorted(set(validation_reasons))
                            st.markdown("<ul style='margin-left:1em;'>" + "".join([f"<li style='margin-bottom:4px;'>{r}</li>" for r in validation_reasons]) + "</ul>", unsafe_allow_html=True)
                        st.write("---")
                        st.write("### Object and variable views:")
                        for doc in docs:
                            st.write(f"**{doc['doc_type']}**:")
                            st.json(doc['obj'].__dict__)
                        st.write("---")
                        st.write("### Download PDFs:")
                        for doc in docs:
                            if doc['pdf_bytes']:
                                st.download_button(
                                    label=f"Download PDF for {doc['doc_type']}",
                                    data=doc['pdf_bytes'],
                                    file_name=doc['pdf_name'] or f"{doc['doc_type'].replace(' ', '_')}.pdf",
                                    mime="application/pdf"
                                )
                        st.write("---")
                        action = st.radio(f"Human Review Action for Loan #{loan_num}", ["Approve", "Deny", "Skip"], key=f"escalate_action_{loan_num}")
                        if st.button(f"Submit Review for Loan #{loan_num}", key=f"submit_escalate_{loan_num}"):
                            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            header = ["timestamp", "reviewer", "loan_number", "doc_type", "action", "confidence_score", "reasons", "pdf_name"]
                            from ai_governance_platform.services.file_management_service import FileManagementService
                            file_service = FileManagementService(base_dir=os.path.dirname(audit_log_path))
                            for doc in docs:
                                log_entry = {
                                    "timestamp": timestamp,
                                    "reviewer": reviewer,
                                    "loan_num": loan_num,
                                    "doc_type": doc['doc_type'],
                                    "action": action,
                                    "score": doc['score'],
                                    "reasons": ", ".join(doc['reasons']),
                                    "pdf_name": doc['pdf_name']
                                }
                                file_service.append_csv(os.path.basename(audit_log_path), log_entry)
                                # Mark document as reviewed
                                if "reviewed_docs" not in st.session_state:
                                    st.session_state["reviewed_docs"] = set()
                                st.session_state["reviewed_docs"].add((loan_num, doc['doc_type']))
                            st.success(f"Action '{action}' recorded for Loan #{loan_num} and logged. All documents for this loan will now be removed from the escalation list.")
                            st.rerun()
    else:
        st.info("No extraction results yet. Run extraction in the first tab.")
        pending_escalations = EscalationService.load_pending_escalations()
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
                    feedback_logger.log_feedback(
                        user=context["user_role"],
                        feedback_type="user",
                        details={
                            "prompt": context["prompt"],
                            "response": response,
                            "feedback": thumbs if thumbs in ["👍", "👎"] else ""
                        }
                    )
                    feedback_gate.summarize_feedback()
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
                from ai_governance_platform.services.file_management_service import FileManagementService
                file_service = FileManagementService(base_dir=os.path.dirname(FEEDBACK_SUMMARY_PATH))
                rows = file_service.read_csv(os.path.basename(FEEDBACK_SUMMARY_PATH))
                header = list(rows[0].keys()) if rows else []
                filtered = [row for row in rows if not (row.get("prompt") == prompt_text and row.get("feedback") == "👎")]
                file_service.write_csv(os.path.basename(FEEDBACK_SUMMARY_PATH), filtered)
                # Rebuild feedback summary
                feedback_gate.summarize_feedback()
                st.success("Downvotes for this prompt have been cleaned up!")

if __name__ == '__main__': main() 