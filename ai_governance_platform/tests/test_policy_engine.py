import pytest
from policy.policy_engine import PolicyEngine
import os

POLICY_PATH = os.path.join(os.path.dirname(__file__), "..", "policy", "policy.yaml")

@pytest.fixture
def engine():
    return PolicyEngine(POLICY_PATH)

def test_hr_salary_access(engine):
    context = {"user_role": "HR", "prompt": "Show me all employee salaries.", "confidence_score": 0.95, "retrieved_sources_present": True}
    decision = engine.apply_policy(context)
    assert decision["decision"] == "allow"

def test_cto_tech_salary(engine):
    context = {"user_role": "CTO", "prompt": "Show me Technology department salaries.", "confidence_score": 0.95, "retrieved_sources_present": True}
    decision = engine.apply_policy(context)
    assert decision["decision"] == "allow"

def test_engineer_own_salary(engine):
    context = {"user_role": "Engineer", "prompt": "Show me my salary.", "confidence_score": 0.95, "retrieved_sources_present": True}
    decision = engine.apply_policy(context)
    assert decision["decision"] == "escalate"

def test_hr_production_deploy(engine):
    context = {"user_role": "HR", "prompt": "How do I deploy to production?", "confidence_score": 0.95, "retrieved_sources_present": True}
    decision = engine.apply_policy(context)
    assert decision["decision"] == "deny"

def test_engineer_all_salaries(engine):
    context = {"user_role": "Engineer", "prompt": "Show me all salaries.", "confidence_score": 0.95, "retrieved_sources_present": True}
    decision = engine.apply_policy(context)
    assert decision["decision"] == "deny"
