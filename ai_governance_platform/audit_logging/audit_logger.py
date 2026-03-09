# AuditLogger implementation
import csv
import os
from datetime import datetime

class AuditLogger:
    def __init__(self, log_path):
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        self.header = [
            "timestamp", "user_role", "prompt", "response", "response_time_ms",
            "confidence_score", "risk_level", "decision", "rule_triggered", "reason", "hil_action", "hil_reviewer"
        ]
        if not os.path.exists(log_path):
            with open(log_path, mode="w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.header)

    def log_interaction(self, entry: dict):
        row = [entry.get(h, "") for h in self.header]
        with open(self.log_path, mode="a", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
            f.flush()
