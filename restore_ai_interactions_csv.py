import csv
import os

CSV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "logs", "ai_interactions.csv"))
OLD_HEADER = [
    "timestamp", "user_role", "prompt", "response", "response_time_ms",
    "confidence_score", "risk_level", "decision", "rule_triggered", "reason", "required_controls", "hil_action", "hil_reviewer"
]

# Remove user_id column and extra empty fields

def restore_csv(csv_path, old_header):
    rows = []
    with open(csv_path, mode="r", newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            # Pad or truncate to old_header length
            if len(row) < len(old_header):
                row = row + ["" for _ in range(len(old_header) - len(row))]
            elif len(row) > len(old_header):
                row = row[:len(old_header)]
            rows.append(row)
    with open(csv_path, mode="w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(old_header)
        for row in rows:
            writer.writerow(row)

if __name__ == "__main__":
    restore_csv(CSV_PATH, OLD_HEADER)
    print("CSV restored to old structure.")
