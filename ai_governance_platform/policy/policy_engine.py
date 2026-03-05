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
        # Default risk is low, but will be set to topic risk if matched
        risk = "low"
        decision = "allow"
        rule_triggered = ""
        reason = ""
        required_controls = []
        # Topic restrictions
        topic_matched = False
        topic_risk = None
        topic_rule = ""
        topic_reason = ""
        for topic in self.policy.get("restricted_topics", []):
            if re.search(topic["pattern"], prompt, re.IGNORECASE):
                topic_risk = topic.get("risk_level", "high")
                topic_rule = f"topic:{topic['name']}"
                topic_reason = f"Prompt matched restricted topic: {topic['name']}"
                topic_matched = True
                if user_role not in topic["allowed_roles"]:
                    decision = "deny"
                    topic_reason = f"Role {user_role} not allowed for topic {topic['name']}"
                    break
        if topic_matched:
            risk = topic_risk
            rule_triggered = topic_rule
            reason = topic_reason
        else:
            rule_triggered = ""
            reason = ""
        # Role permissions
        if decision == "allow":
            perms = self.policy.get("role_permissions", {}).get(user_role, {})
            if perms:
                # Engineer: allow 'my salary' or 'own salary', deny 'all salaries' etc.
                allow_patterns = perms.get("allow_patterns", [])
                denied = False
                allowed = False
                for ap in allow_patterns:
                    if re.search(ap, prompt, re.IGNORECASE):
                        allowed = True
                        break
                for p in perms.get("deny_patterns", []):
                    if re.search(p, prompt, re.IGNORECASE):
                        denied = True
                        break
                if denied and not allowed:
                    decision = "deny"
                    rule_triggered = f"role:{user_role}_denied:{p}"
                    reason = f"Role {user_role} denied for pattern {p}"
                elif allowed:
                    decision = "allow"
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
        result = {
            "decision": decision,
            "risk_level": risk,
            "rule_triggered": rule_triggered,
            "reason": reason,
            "required_controls": required_controls
        }
        print("[DEBUG] apply_policy context:", context)
        print("[DEBUG] apply_policy result:", result)
        return result
