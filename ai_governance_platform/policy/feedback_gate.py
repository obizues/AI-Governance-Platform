import hashlib
import json
import os

class FeedbackGate:
    def __init__(self, summary_path):
        self.summary_path = summary_path

    def apply_feedback_gate(self, context, policy_engine):
        prompt_hash = context.get("prompt_hash")
        downvotes = 0
        if os.path.exists(self.summary_path):
            try:
                with open(self.summary_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if not content:
                        summary = {}
                    else:
                        summary = json.loads(content)
                downvotes = summary.get(prompt_hash, {}).get("down", 0)
            except (json.JSONDecodeError, FileNotFoundError):
                summary = {}
                downvotes = 0
        if downvotes >= 2:
            return {
                "decision": "escalate",
                "risk_level": "high",
                "rule_triggered": "feedback_gate",
                "reason": "Prompt received repeated negative feedback.",
                "required_controls": []
            }
        return policy_engine.apply_policy(context)
