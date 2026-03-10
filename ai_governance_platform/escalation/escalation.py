def load_all_escalation_logs():
    """Load all escalation logs from ai_interactions.csv, including reviewed and unreviewed."""
    df = pd.read_csv(ESCALATION_CSV)
    logs = df[df['rule_triggered'] == 'escalate']
    return logs
"""
escalation.py: Handles escalation review logic, CSV parsing, and HIL actions for the AI Governance Platform.
"""
import csv
import os
import pandas as pd

ESCALATION_CSV = os.path.join(os.path.dirname(__file__), '../../logs/ai_interactions.csv')
HIL_ACTIONS_CSV = os.path.join(os.path.dirname(__file__), '../../logs/hil_actions.csv')


def load_pending_escalations():
    """Load pending escalations from ai_interactions.csv."""
    df = pd.read_csv(ESCALATION_CSV)
    # Ensure all expected columns exist
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
    # Print debug info
    print("[DEBUG] Escalation CSV shape:", df.shape)
    print("[DEBUG] Columns:", df.columns.tolist())
    print("[DEBUG] Unique values - rule_triggered:", df['rule_triggered'].unique())
    print("[DEBUG] Unique values - decision:", df['decision'].unique())
    print("[DEBUG] Unique values - hil_action:", df['hil_action'].unique())
    # Print sample rows where escalate is present
    escalate_rows = df[df['rule_triggered'].str.contains('escalate') | df['decision'].str.contains('escalate')]
    print("[DEBUG] Sample escalate rows:")
    print(escalate_rows[['timestamp','rule_triggered','decision','hil_action']].head(10))
    # Pending: rule_triggered contains 'escalate', decision == 'escalate', hil_action == ''
    pending = df[df['rule_triggered'].str.contains('escalate') & (df['decision'] == 'escalate') & (df['hil_action'] == '')]
    print("[DEBUG] Pending escalations shape:", pending.shape)
    print("[DEBUG] Pending escalation values:")
    if not pending.empty:
        print(pending[['timestamp','rule_triggered','decision','hil_action']].head(10))
    return pending


def log_hil_action(timestamp, reviewer, action, prompt, risk_level):
    """Log HIL action to hil_actions.csv."""
    # Log to hil_actions.csv
    with open(HIL_ACTIONS_CSV, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, reviewer, action])
    # Update ai_interactions.csv hil_action for this escalation
    import pandas as pd
    df = pd.read_csv(ESCALATION_CSV)
    # Ensure hil_action column exists and is string dtype
    if 'hil_action' not in df.columns:
        df['hil_action'] = ''
    df['hil_action'] = df['hil_action'].astype(str)
    # Ensure hil_reviewer column exists and is string dtype
    if 'hil_reviewer' not in df.columns:
        df['hil_reviewer'] = ''
    df = df.astype({'hil_reviewer': 'object'})
    # Update escalation row by timestamp, prompt, and risk_level
    # Use actual values for prompt and risk_level
    # Accept prompt and risk_level as arguments
    # Patch: match row by exact values for timestamp, prompt, risk_level
    # Patch: match only by timestamp for reliability
    mask = (df['timestamp'].astype(str) == str(timestamp))
    df.loc[mask, 'hil_action'] = action.lower()
    df.loc[mask, 'hil_reviewer'] = str(reviewer)
    if action.lower() in ['approve', 'deny']:
        df.loc[mask, 'decision'] = action.lower()
    df.to_csv(ESCALATION_CSV, index=False)


def get_unique_key(row):
    """Generate a unique key for a row using timestamp and prompt."""
    return f"{row['timestamp']}_{hash(row['prompt'])}"

