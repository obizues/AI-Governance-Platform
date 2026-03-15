import copy

from ai_governance_platform.services.feedback_service import FeedbackService


def _valid_record():
    return {
        "package_id": "PKG-001",
        "loan_package": "LoanA",
        "document_type": "bank_statement",
        "field_name": "monthly_income",
        "model_prediction": "5000",
        "corrected_value": "5200",
        "decision": "does_not_match",
        "reason_code": "manual_correction",
        "comment": "Applicant provided updated document.",
        "reviewer": "analyst-1",
        "timestamp": "2026-03-14T09:30:00",
        "model_version": "v0.11.1",
        "run_id": "run-1001",
        "source_tab": "human_feedback",
    }


def test_submit_feedback_persists_valid_record(tmp_path):
    service = FeedbackService(log_dir=str(tmp_path))

    result = service.submit_feedback(_valid_record())

    assert result["success"] is True
    assert result["duplicate"] is False
    entries = service.list_feedback()
    assert len(entries) == 1
    assert entries[0]["package_id"] == "PKG-001"
    assert entries[0]["idempotency_key"]


def test_submit_feedback_rejects_missing_required_fields(tmp_path):
    service = FeedbackService(log_dir=str(tmp_path))
    record = _valid_record()
    record["package_id"] = ""

    result = service.submit_feedback(record)

    assert result["success"] is False
    assert "package_id is required" in result["errors"]
    assert service.list_feedback() == []


def test_submit_feedback_requires_comment_for_does_not_match(tmp_path):
    service = FeedbackService(log_dir=str(tmp_path))
    record = _valid_record()
    record["comment"] = ""
    record["decision"] = "does_not_match"

    result = service.submit_feedback(record)

    assert result["success"] is False
    assert "comment is required when the value does not match the document (cite your evidence)" in result["errors"]


def test_submit_feedback_cannot_verify_does_not_require_comment(tmp_path):
    service = FeedbackService(log_dir=str(tmp_path))
    record = _valid_record()
    record["comment"] = ""
    record["decision"] = "cannot_verify"

    result = service.submit_feedback(record)

    assert result["success"] is True


def test_submit_feedback_rejects_invalid_source_tab(tmp_path):
    service = FeedbackService(log_dir=str(tmp_path))
    record = _valid_record()
    record["source_tab"] = "monitoring"

    result = service.submit_feedback(record)

    assert result["success"] is False
    assert any("source_tab must be one of" in err for err in result["errors"])


def test_submit_feedback_is_idempotent_for_duplicate_payload(tmp_path):
    service = FeedbackService(log_dir=str(tmp_path))
    record = _valid_record()

    first = service.submit_feedback(record)
    second = service.submit_feedback(copy.deepcopy(record))

    assert first["success"] is True
    assert first["duplicate"] is False
    assert second["success"] is True
    assert second["duplicate"] is True
    assert len(service.list_feedback()) == 1


def test_submit_feedback_allows_empty_model_prediction(tmp_path):
    service = FeedbackService(log_dir=str(tmp_path))
    record = _valid_record()
    record["model_prediction"] = ""
    record["corrected_value"] = "12345"

    result = service.submit_feedback(record)

    assert result["success"] is True
    entries = service.list_feedback()
    assert len(entries) == 1
    assert entries[0]["model_prediction"] == ""
    assert entries[0]["corrected_value"] == "12345"


def test_submit_feedback_normalizes_legacy_decision_aliases(tmp_path):
    service = FeedbackService(log_dir=str(tmp_path))

    record = _valid_record()
    record["decision"] = "corrected"
    result = service.submit_feedback(record)

    assert result["success"] is True
    saved = service.list_feedback()
    assert len(saved) == 1
    assert saved[0]["decision"] == "does_not_match"


def test_feedback_summary_counts_by_dimensions(tmp_path):
    service = FeedbackService(log_dir=str(tmp_path))

    first = _valid_record()
    second = _valid_record()
    second["package_id"] = "PKG-002"
    second["loan_package"] = "LoanB"
    second["field_name"] = "loan_amount"
    second["decision"] = "approve"
    second["reason_code"] = "verified"
    second["comment"] = ""
    second["timestamp"] = "2026-03-14T09:35:00"
    second["source_tab"] = "escalation_review"

    service.submit_feedback(first)
    service.submit_feedback(second)

    summary = service.feedback_summary()

    assert summary["total"] == 2
    assert summary["by_decision"]["does_not_match"] == 1
    assert summary["by_decision"]["approve"] == 1
    assert summary["by_source_tab"]["human_feedback"] == 1
    assert summary["by_source_tab"]["escalation_review"] == 1


def test_list_feedback_supports_time_range_and_multi_value_filters(tmp_path):
    service = FeedbackService(log_dir=str(tmp_path))

    first = _valid_record()
    second = _valid_record()
    second["package_id"] = "PKG-002"
    second["loan_package"] = "LoanB"
    second["source_tab"] = "escalation_review"
    second["field_name"] = "loan_amount"
    second["timestamp"] = "2026-03-14T10:30:00"

    service.submit_feedback(first)
    service.submit_feedback(second)

    filtered = service.list_feedback(
        filters={
            "source_tab": ["human_feedback", "escalation_review"],
            "timestamp_from": "2026-03-14T10:00:00",
            "timestamp_to": "2026-03-14T11:00:00",
        }
    )

    assert len(filtered) == 1
    assert filtered[0]["package_id"] == "PKG-002"


def test_export_training_labels_exports_eligible_deduped_rows(tmp_path):
    service = FeedbackService(log_dir=str(tmp_path))

    confirmed = _valid_record()
    confirmed["decision"] = "matches_document"
    confirmed["comment"] = ""

    unverifiable = _valid_record()
    unverifiable["package_id"] = "PKG-002"
    unverifiable["loan_package"] = "LoanB"
    unverifiable["field_name"] = "loan_amount"
    unverifiable["decision"] = "cannot_verify"
    unverifiable["comment"] = ""
    unverifiable["timestamp"] = "2026-03-14T09:40:00"

    service.submit_feedback(confirmed)
    service.submit_feedback(confirmed)
    service.submit_feedback(unverifiable)

    exported = service.export_training_labels()

    assert exported["total_input_rows"] == 2
    assert exported["total_exported_labels"] == 1
    assert exported["labels"][0]["decision"] == "matches_document"
    assert exported["labels"][0]["label_value"] == confirmed["corrected_value"]
    assert exported["skipped"]["ineligible_decision"] == 1


def test_export_training_labels_excludes_escalation_review_by_default(tmp_path):
    service = FeedbackService(log_dir=str(tmp_path))

    human_row = _valid_record()
    human_row["decision"] = "matches_document"
    human_row["comment"] = ""

    escalation_row = _valid_record()
    escalation_row["package_id"] = "PKG-777"
    escalation_row["loan_package"] = "LoanZ"
    escalation_row["field_name"] = "loan_amount"
    escalation_row["decision"] = "approve"
    escalation_row["reason_code"] = "escalation_approved"
    escalation_row["comment"] = ""
    escalation_row["source_tab"] = "escalation_review"
    escalation_row["timestamp"] = "2026-03-14T11:45:00"

    service.submit_feedback(human_row)
    service.submit_feedback(escalation_row)

    exported = service.export_training_labels()

    assert exported["total_input_rows"] == 1
    assert exported["total_exported_labels"] == 1
    assert exported["labels"][0]["source_tab"] == "human_feedback"
