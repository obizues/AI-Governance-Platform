import time
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'audit_logging'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'feedback'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'evaluation'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'policy'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'providers'))
from ai_governance_platform.audit_logging.audit_logger import AuditLogger
from ai_governance_platform.feedback.feedback_logger import FeedbackLogger
from ai_governance_platform.evaluation.evaluation_runner import EvaluationRunner
from ai_governance_platform.policy.policy_engine import PolicyEngine
from ai_governance_platform.providers.provider_interface import StubProvider

BASE_DIR = os.path.dirname(__file__)
LOG_PATH = os.path.join(BASE_DIR, "..", "logs", "ai_interactions.csv")
FEEDBACK_PATH = os.path.join(BASE_DIR, "..", "logs", "feedback_log.csv")
POLICY_PATH = os.path.join(BASE_DIR, "policy", "policy.yaml")
EVAL_DATASET_PATH = os.path.join(BASE_DIR, "evaluation", "evaluation_dataset.json")
EVAL_REPORT_PATH = os.path.join(BASE_DIR, "evaluation", "evaluation_report.json")

def run_interactive():
    print("--- Interactive Request ---")
    user_id = "user123"
    user_role = "HR"
    prompt = "Show me all employee salaries."
    provider = StubProvider()
    policy_engine = PolicyEngine(POLICY_PATH)
    audit_logger = AuditLogger(LOG_PATH)
    feedback_logger = FeedbackLogger(FEEDBACK_PATH)
    start = time.time()
    response = provider.generate_response(prompt)
    response_time_ms = int((time.time() - start) * 1000)
    confidence_score = 0.95
    context = {
        "user_id": user_id,
        "user_role": user_role,
        "prompt": prompt,
        "response": response,
        "confidence_score": confidence_score,
        "retrieved_sources_present": True
    }
    decision = policy_engine.apply_policy(context)
    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": user_id,
        "user_role": user_role,
        "prompt": prompt,
        "response": response if decision["decision"] == "allow" else "[REFUSAL] Access Denied.",
        "response_time_ms": response_time_ms,
        "confidence_score": confidence_score,
        "risk_level": decision["risk_level"],
        "decision": decision["decision"],
        "rule_triggered": decision["rule_triggered"],
        "reason": decision["reason"],
        "required_controls": ",".join(decision["required_controls"])
    }
    audit_logger.log_interaction(entry)
    print(f"Prompt: {prompt}\nResponse: {entry['response']}\nDecision: {decision['decision']}")
    feedback = input("Was this response correct? (👍/👎): ")
    feedback_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "user_role": user_role,
        "prompt": prompt,
        "response": entry["response"],
        "feedback": feedback
    }
    feedback_logger.log_feedback(feedback_entry)

def run_evaluation():
    print("--- Running Evaluation ---")
    provider = StubProvider()
    policy_engine = PolicyEngine(POLICY_PATH)
    runner = EvaluationRunner(EVAL_DATASET_PATH, EVAL_REPORT_PATH)
    runner.run(provider, policy_engine)
    print(f"Evaluation report generated at {EVAL_REPORT_PATH}")

def main():
    run_interactive()
    run_evaluation()

if __name__ == "__main__":
    main()
