import csv
import os
from datetime import datetime
import logging

debug_path = os.path.join(os.path.dirname(__file__), '..', '..', 'logs', 'debug.txt')
logging.basicConfig(filename=debug_path, level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

class FeedbackLogger:
    def __init__(self, log_path):
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        self.header = ["timestamp", "user_role", "prompt", "response", "feedback"]
        # Always ensure header exists if file is empty
        if not os.path.exists(log_path) or os.stat(log_path).st_size == 0:
            with open(log_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self.header)
        # Test debug.txt write
        debug_path = os.path.join(os.path.dirname(__file__), '..', '..', 'logs', 'debug.txt')
        try:
            with open(debug_path, mode="a", encoding="utf-8") as dbg:
                dbg.write("DEBUG: FeedbackLogger initialized\n")
        except Exception as e:
            print(f"ERROR: Could not write to debug.txt: {e}")

    def log_feedback(self, entry: dict):
        row = [entry.get(h, "") for h in self.header]
        debug_path = os.path.join(os.path.dirname(__file__), '..', '..', 'logs', 'debug.txt')
        try:
            with open(debug_path, mode="a", encoding="utf-8") as dbg:
                dbg.write(f"DEBUG: log_feedback called with row: {row}\n")
            with open(self.log_path, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(row)
                f.flush()
            with open(debug_path, mode="a", encoding="utf-8") as dbg:
                dbg.write(f"DEBUG: Wrote feedback row: {row} to {self.log_path}\n")
        except Exception as e:
            import streamlit as st
            st.warning(f"Feedback logging failed: {e}")
            with open(debug_path, mode="a", encoding="utf-8") as dbg:
                dbg.write(f"ERROR: Feedback logging failed: {e}\n")
