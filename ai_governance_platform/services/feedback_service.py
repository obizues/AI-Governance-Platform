"""
Feedback Handling Service Module
Centralizes feedback collection, logging, and summarization for the AI Governance Platform.
"""

import os
import csv
from datetime import datetime

class FeedbackService:
    def __init__(self, log_dir="logs", log_file="feedback_log.csv"):
        self.log_dir = log_dir
        self.log_file = log_file
        self.log_path = os.path.join(self.log_dir, self.log_file)
        os.makedirs(self.log_dir, exist_ok=True)

    def log_feedback(self, user, feedback_type, details):
        """
        Logs feedback to the CSV log file.
        Args:
            user (str): User or system actor.
            feedback_type (str): Type of feedback (e.g., 'user', 'system', 'review').
            details (dict): Additional feedback details.
        """
        timestamp = datetime.utcnow().isoformat()
        row = {
            "timestamp": timestamp,
            "user": user,
            "feedback_type": feedback_type,
            **details
        }
        write_header = not os.path.exists(self.log_path)
        with open(self.log_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if write_header:
                writer.writeheader()
            writer.writerow(row)

    def get_feedback(self, filter_type=None):
        """
        Retrieves feedback logs, optionally filtered by feedback type.
        Args:
            filter_type (str, optional): Filter feedback by type.
        Returns:
            List[dict]: List of feedback entries.
        """
        if not os.path.exists(self.log_path):
            return []
        with open(self.log_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            feedback = [row for row in reader]
        if filter_type:
            feedback = [fb for fb in feedback if fb["feedback_type"] == filter_type]
        return feedback

    def summarize_feedback(self):
        """
        Summarizes feedback entries for reporting or analytics.
        Returns:
            dict: Summary statistics (counts, types, etc.)
        """
        feedback = self.get_feedback()
        summary = {}
        for fb in feedback:
            ftype = fb.get("feedback_type", "unknown")
            summary[ftype] = summary.get(ftype, 0) + 1
        return summary

def collect_feedback(document):
    # Human feedback logic stub
    return {'status': 'feedback_collected', 'feedback': 'Sample feedback'}
