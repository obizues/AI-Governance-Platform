"""
EscalationService: Handles escalation review logic, CSV parsing, and HIL actions for the AI Governance Platform.
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
