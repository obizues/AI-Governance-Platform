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
    # Normalize hil_action values
    df['hil_action'] = df['hil_action'].fillna('').astype(str).str.strip()
    pending = df[(df['rule_triggered'] == 'escalate') & (~df['hil_action'].isin(['approve', 'deny']))]
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

