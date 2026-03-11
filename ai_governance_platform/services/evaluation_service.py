"""
EvaluationService: Handles evaluation dataset loading, running, scoring, and report generation for the AI Governance Platform.
"""
import json
from typing import List

class EvaluationService:
    def __init__(self, dataset_path, report_path):
        self.dataset_path = dataset_path
        self.report_path = report_path
        with open(dataset_path, "r", encoding="utf-8") as f:
            self.dataset = json.load(f)
        self.results = []

    def score_response(self, response: str, expected_keywords: List[str]) -> int:
        return sum(1 for kw in expected_keywords if kw.lower() in response.lower())

    def run(self, provider, policy_service):
        for case in self.dataset:
            context = {
                "user_role": case["user_role"],
                "user_id": case.get("user_id", "test_user"),
                "prompt": case["question"],
                "confidence_score": 1.0,
                "retrieved_sources_present": True,
            }
            response = provider.generate_response(context["prompt"])
            context["response"] = response
            decision = policy_service.apply_policy(context)
            score = self.score_response(response, case["expected_keywords"])
            passed = (decision["decision"] == case["expected_decision"])
            self.results.append({
                "test_id": case["test_id"],
                "user_role": case["user_role"],
                "question": case["question"],
                "response": response,
                "score": score,
                "passed": passed,
                "decision": decision["decision"],
                "expected_decision": case["expected_decision"]
            })
        self.generate_report()

    def generate_report(self):
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        avg_score = sum(r["score"] for r in self.results) / total if total else 0
        failures = [r for r in self.results if not r["passed"]]
        report = {
            "summary": {
                "total": total,
                "pass_rate": passed / total if total else 0,
                "average_score": avg_score,
                "failures": failures
            },
            "results": self.results
        }
        with open(self.report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        return report
