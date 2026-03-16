"""
EscalationService: Handles escalation review logic, CSV parsing, and HIL actions for the AI Document Governance Platform.
"""
import csv
import os
import pandas as pd

ESCALATION_CSV = os.path.join(os.path.dirname(__file__), '../../logs/ai_interactions.csv')
HIL_ACTIONS_CSV = os.path.join(os.path.dirname(__file__), '../../logs/hil_actions.csv')

class EscalationService:
    @staticmethod
    def load_all_escalation_logs():
        df = pd.read_csv(ESCALATION_CSV)
        logs = df[df['rule_triggered'] == 'escalate']
        return logs

    @staticmethod
    def load_pending_escalations():
        df = pd.read_csv(ESCALATION_CSV)
        expected_cols = [
            "timestamp", "user_role", "prompt", "response", "response_time_ms",
            "confidence_score", "risk_level", "decision", "rule_triggered", "reason",
            "required_controls", "hil_action", "hil_reviewer"
        ]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = ''
        for col in ['hil_action', 'rule_triggered', 'decision']:
            df[col] = df[col].fillna('').astype(str).str.strip().str.lower()
        # Show all rows with rule_triggered == 'escalate' and hil_action == ''
        pending = df[(df['rule_triggered'] == 'escalate') & (df['hil_action'] == '')]
        return pending

    @staticmethod
    def log_hil_action(timestamp, reviewer, action, prompt, risk_level):
        with open(HIL_ACTIONS_CSV, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, reviewer, action])
        df = pd.read_csv(ESCALATION_CSV)
        if 'hil_action' not in df.columns:
            df['hil_action'] = ''
        df['hil_action'] = df['hil_action'].astype(str)
        if 'hil_reviewer' not in df.columns:
            df['hil_reviewer'] = ''
        df = df.astype({'hil_reviewer': 'object'})
        # Mark only the specific escalation row as reviewed
        mask = (
            df['timestamp'].astype(str) == str(timestamp)
        ) & (
            df['prompt'].astype(str) == str(prompt)
        ) & (
            df['loan_package'].astype(str) == str(risk_level)
        )
        df.loc[mask, 'hil_action'] = action.lower()
        df.loc[mask, 'hil_reviewer'] = str(reviewer)
        if action.lower() in ['approve', 'deny']:
            df.loc[mask, 'decision'] = action.lower()
        df.to_csv(ESCALATION_CSV, index=False)

    @staticmethod
    def get_unique_key(row):
        return f"{row['timestamp']}_{hash(row['prompt'])}"

    @staticmethod
    def escalate_review(document):
        # Escalation review logic stub
        return {'status': 'escalated', 'reason': 'Low confidence'}

    # ── Utility helpers for app.py / feedback flow ────────────────────────

    @staticmethod
    def extract_escalated_field(reason: str) -> str:
        """
        Parse the field name from a reason string like
        'balance below confidence threshold (0.62)'.
        Returns the field name (with underscores) or empty string.
        """
        reason = str(reason or "").strip()
        if "below confidence threshold" in reason:
            return reason.split("below confidence threshold")[0].strip().replace(" ", "_")
        return ""

    @staticmethod
    def normalize_document_type(document_name: str) -> str:
        """Convert a PDF filename to a normalised document_type slug."""
        return str(document_name or "").replace(".pdf", "").replace(" ", "_").lower()

    @staticmethod
    def build_governance_feedback_payload(
        row,
        action: str,
        reviewer: str,
        comment: str,
        active_model_version: str,
        escalated_field: str = "",
        escalated_value: str = "",
    ) -> dict:
        """
        Build the feedback_payload dict for escalation-review governance logging.
        `row` is a pandas Series (one row from the pending escalations DataFrame).
        """
        package_id = str(row.get("loan_package", "")).strip()
        document_name = str(row.get("prompt", "")).strip()
        document_type = document_name.replace(".pdf", "").replace(" ", "_").lower()
        field_name = str(escalated_field or "unknown_field").strip() or "unknown_field"
        action_lower = str(action).strip().lower()
        return {
            "package_id": package_id,
            "loan_package": package_id,
            "document_type": document_type,
            "field_name": field_name,
            "model_prediction": str(escalated_value or "").strip(),
            "corrected_value": str(escalated_value or "").strip() if action_lower == "approve" else "",
            "decision": action_lower,
            "reason_code": "escalation_approved" if action_lower == "approve" else "escalation_denied",
            "comment": comment,
            "reviewer": reviewer,
            "timestamp": str(row.get("timestamp", "")).strip(),
            "model_version": active_model_version,
            "run_id": f"{package_id}_{row.get('timestamp', '')}",
            "source_tab": "escalation_review",
        }
