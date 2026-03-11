"""
Audit Logging Service Module
Centralizes audit logging logic for the AI Governance Platform.
"""

import os
import csv
from datetime import datetime

class AuditLoggingService:
    def __init__(self, log_dir="logs", log_file="ai_interactions.csv"):
        self.log_dir = log_dir
        self.log_file = log_file
        self.log_path = os.path.join(self.log_dir, self.log_file)
        os.makedirs(self.log_dir, exist_ok=True)

    def log_event(self, event_type, user, details):
        """
        Logs an audit event to the CSV log file.
        Args:
            event_type (str): Type of event (e.g., 'extraction', 'validation', 'feedback').
            user (str): User or system actor.
            details (dict): Additional event details.
        """
        timestamp = datetime.utcnow().isoformat()
        row = {
            "timestamp": timestamp,
            "event_type": event_type,
            "user": user,
            **details
        }
        write_header = not os.path.exists(self.log_path)
        with open(self.log_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if write_header:
                writer.writeheader()
            writer.writerow(row)

    def get_logs(self, filter_type=None):
        """
        Retrieves audit logs, optionally filtered by event type.
        Args:
            filter_type (str, optional): Filter logs by event type.
        Returns:
            List[dict]: List of log entries.
        """
        if not os.path.exists(self.log_path):
            return []
        with open(self.log_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            logs = [row for row in reader]
        if filter_type:
            logs = [log for log in logs if log["event_type"] == filter_type]
        return logs
