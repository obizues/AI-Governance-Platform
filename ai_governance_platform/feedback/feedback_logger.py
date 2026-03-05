import csv
import os
from datetime import datetime

class FeedbackLogger:
    def __init__(self, log_path):
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        self.header = ["timestamp", "user_role", "prompt", "response", "feedback"]
        if not os.path.exists(log_path):
            with open(log_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self.header)

    def log_feedback(self, entry: dict):
        row = [entry.get(h, "") for h in self.header]
        with open(self.log_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)
