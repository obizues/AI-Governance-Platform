import csv
import json
import hashlib
import os

class FeedbackSummary:
    def __init__(self, feedback_path, summary_path):
        self.feedback_path = feedback_path
        self.summary_path = summary_path

    def rebuild_summary(self):
        summary = {}
        if not os.path.exists(self.feedback_path):
            with open(self.summary_path, "w", encoding="utf-8") as f:
                json.dump(summary, f)
            return
        with open(self.feedback_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                prompt_hash = hashlib.sha256(row["prompt"].encode()).hexdigest()
                if prompt_hash not in summary:
                    summary[prompt_hash] = {"up": 0, "down": 0, "prompts": set()}
                if row["feedback"] == "👍":
                    summary[prompt_hash]["up"] += 1
                elif row["feedback"] == "👎":
                    summary[prompt_hash]["down"] += 1
                summary[prompt_hash]["prompts"].add(row["prompt"])
        # Convert sets to lists for JSON serialization
        for h in summary:
            summary[h]["prompts"] = list(summary[h]["prompts"])
        with open(self.summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

    def get_downvotes(self, prompt_hash):
        if not os.path.exists(self.summary_path):
            return 0
        with open(self.summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)
        return summary.get(prompt_hash, {}).get("down", 0)
