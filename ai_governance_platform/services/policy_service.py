"""
Policy Engine Service Module
Centralizes policy evaluation and risk assessment logic for the AI Governance Platform.
"""

import yaml
import os
from typing import Any, Dict

class PolicyService:
    def __init__(self, policy_path="policy/policy.yaml"):
        self.policy_path = policy_path
        self.policy = self.load_policy()

    def load_policy(self) -> Dict[str, Any]:
        if not os.path.exists(self.policy_path):
            return {}
        with open(self.policy_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def evaluate(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a query against the policy rules.
        Args:
            query (str): The user/system query to evaluate.
            context (dict): Additional context for evaluation.
        Returns:
            dict: Evaluation result (risk, decision, rule_triggered, reason).
        """
        # Example logic: match query keywords to policy rules
        result = {
            "risk": "low",
            "decision": "approve",
            "rule_triggered": None,
            "reason": "No risk detected."
        }
        for rule in self.policy.get("rules", []):
            keywords = rule.get("keywords", [])
            if any(kw.lower() in query.lower() for kw in keywords):
                result["risk"] = rule.get("risk", "medium")
                result["decision"] = rule.get("decision", "review")
                result["rule_triggered"] = rule.get("name", "unknown")
                result["reason"] = rule.get("reason", "Triggered by policy keyword.")
                break
        return result

    def get_policy_summary(self) -> Dict[str, Any]:
        """
        Returns a summary of the loaded policy.
        """
        return {
            "policy_path": self.policy_path,
            "rules_count": len(self.policy.get("rules", [])),
            "rules": self.policy.get("rules", [])
        }
