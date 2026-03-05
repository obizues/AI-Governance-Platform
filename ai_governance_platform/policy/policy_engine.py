import yaml
import re

class PolicyEngine:
    def __init__(self, policy_path):
        with open(policy_path, "r", encoding="utf-8") as f:
            self.policy = yaml.safe_load(f)

    def risk_score(self, prompt, response, confidence_score):
        risk = "low"
        for topic in self.policy.get("restricted_topics", []):
            if re.search(topic["pattern"], prompt, re.IGNORECASE):
                risk = topic.get("risk_level", "high")
        if confidence_score < self.policy.get("minimum_confidence", 0.7):
            risk = max(risk, "medium")
        return risk

    def apply_policy(self, context):
        user_role = context["user_role"]
        prompt = context["prompt"]
        response = context.get("response", "")
        confidence_score = context.get("confidence_score", 1.0)
        retrieved_sources_present = context.get("retrieved_sources_present", False)
        risk = self.risk_score(prompt, response, confidence_score)
        decision = "allow"
        rule_triggered = ""
        reason = ""
        required_controls = []
        # Topic restrictions
        for topic in self.policy.get("restricted_topics", []):
            if re.search(topic["pattern"], prompt, re.IGNORECASE):
                if user_role not in topic["allowed_roles"]:
                    decision = "deny"
                    rule_triggered = f"topic:{topic['name']}"
                    reason = f"Role {user_role} not allowed for topic {topic['name']}"
                    break
        # Role permissions
        if decision == "allow":
            perms = self.policy.get("role_permissions", {}).get(user_role, {})
            if perms:
                for p in perms.get("deny_patterns", []):
                    if re.search(p, prompt, re.IGNORECASE):
                        decision = "deny"
                        rule_triggered = f"role:{user_role}_denied:{p}"
                        reason = f"Role {user_role} denied for pattern {p}"
                        break
        # Confidence threshold
        if decision == "allow" and confidence_score < self.policy.get("minimum_confidence", 0.7):
            if self.policy.get("controls", {}).get("refuse_low_confidence", True):
                decision = "deny"
                rule_triggered = "confidence:low"
                reason = "Low confidence response denied"
            else:
                decision = "allow_with_controls"
                required_controls.append("require_citations")
                rule_triggered = "confidence:low"
                reason = "Low confidence, controls required"
        # Controls enforcement
        if decision == "allow_with_controls":
            if "require_citations" in required_controls and not retrieved_sources_present:
                decision = "escalate"
                rule_triggered = "controls:citations_missing"
                reason = "Required citations missing"
        # Escalate high risk
        if risk == "high" and decision == "allow":
            if self.policy.get("controls", {}).get("escalate_high_risk", True):
                decision = "escalate"
                rule_triggered = "risk:high"
                reason = "High risk prompt escalated"
        return {
            "decision": decision,
            "risk_level": risk,
            "rule_triggered": rule_triggered,
            "reason": reason,
            "required_controls": required_controls
        }
