"""Feedback handling service with normalized contract and validation rules."""

import hashlib
from datetime import UTC, datetime
from typing import Any

from ai_governance_platform.services.file_management_service import FileManagementService


class FeedbackService:
    FEEDBACK_FIELDS = [
        "package_id",
        "loan_package",
        "document_type",
        "field_name",
        "model_prediction",
        "corrected_value",
        "decision",
        "reason_code",
        "comment",
        "reviewer",
        "timestamp",
        "model_version",
        "run_id",
        "source_tab",
        "idempotency_key",
    ]

    REQUIRED_NON_EMPTY_FIELDS = {
        "package_id",
        "loan_package",
        "document_type",
        "field_name",
        "decision",
        "reason_code",
        "reviewer",
        "timestamp",
        "model_version",
        "run_id",
        "source_tab",
    }

    # Escalation Review tab: approve / deny  (operational proceed/block)
    # Human Feedback tab:    matches_document / does_not_match / cannot_verify
    #   Reviewer opens the source PDF and answers: does the document show the same value the model extracted?
    VALID_DECISIONS = {"approve", "deny", "matches_document", "does_not_match", "cannot_verify"}
    LEGACY_DECISION_ALIASES = {
        "confirmed": "matches_document",
        "corrected": "does_not_match",
        "unverifiable": "cannot_verify",
        "low_confidence_approve": "matches_document",
    }
    VALID_SOURCE_TABS = {"escalation_review", "human_feedback"}
    # Only Human Feedback decisions with known ground truth are training-eligible.
    # Escalation review decisions are governance controls and are excluded from model training labels.
    TRAINING_ELIGIBLE_DECISIONS = {"matches_document", "does_not_match"}

    def __init__(self, log_dir="logs", log_file="feedback_log.csv"):
        self.log_dir = log_dir
        self.log_file = log_file
        self.file_service = FileManagementService(base_dir=self.log_dir)

    @staticmethod
    def _normalize_value(value):
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        return str(value)

    def _canonicalize_decision(self, decision: str) -> str:
        raw = self._normalize_value(decision).lower()
        return self.LEGACY_DECISION_ALIASES.get(raw, raw)

    def _normalize_record(self, record):
        normalized = {field: self._normalize_value(record.get(field, "")) for field in self.FEEDBACK_FIELDS}
        normalized["decision"] = self._canonicalize_decision(normalized["decision"])
        normalized["source_tab"] = normalized["source_tab"].lower()
        if not normalized["timestamp"]:
            normalized["timestamp"] = datetime.now(UTC).isoformat()
        return normalized

    @staticmethod
    def _is_iso_timestamp(value):
        try:
            datetime.fromisoformat(value)
            return True
        except ValueError:
            return False

    def _build_idempotency_key(self, record):
        fingerprint_parts = [
            record["package_id"],
            record["loan_package"],
            record["document_type"],
            record["field_name"],
            record["model_prediction"],
            record["corrected_value"],
            record["decision"],
            record["reason_code"],
            record["reviewer"],
            record["timestamp"],
            record["model_version"],
            record["run_id"],
            record["source_tab"],
        ]
        joined = "|".join(fingerprint_parts)
        return hashlib.sha256(joined.encode("utf-8")).hexdigest()

    def _validate_feedback_record(self, record):
        errors = []

        for field in sorted(self.REQUIRED_NON_EMPTY_FIELDS):
            if not record.get(field):
                errors.append(f"{field} is required")

        decision = record.get("decision", "")
        if decision and decision not in self.VALID_DECISIONS:
            errors.append(
                f"decision must be one of: {', '.join(sorted(self.VALID_DECISIONS))}"
            )

        source_tab = record.get("source_tab", "")
        if source_tab and source_tab not in self.VALID_SOURCE_TABS:
            errors.append(
                f"source_tab must be one of: {', '.join(sorted(self.VALID_SOURCE_TABS))}"
            )

        if record.get("timestamp") and not self._is_iso_timestamp(record["timestamp"]):
            errors.append("timestamp must be a valid ISO-8601 datetime string")

        if record.get("decision") == "does_not_match" and not record.get("comment"):
            errors.append("comment is required when the value does not match the document (cite your evidence)")

        return errors

    def submit_feedback(self, record):
        normalized = self._normalize_record(record)
        validation_errors = self._validate_feedback_record(normalized)
        if validation_errors:
            return {
                "success": False,
                "errors": validation_errors,
                "record": normalized,
            }

        normalized["idempotency_key"] = self._build_idempotency_key(normalized)
        existing = self.file_service.read_csv(self.log_file)
        existing_keys = {row.get("idempotency_key", "") for row in existing}
        if normalized["idempotency_key"] in existing_keys:
            return {
                "success": True,
                "duplicate": True,
                "record": normalized,
            }

        self.file_service.append_csv(
            self.log_file,
            normalized,
            fieldnames=self.FEEDBACK_FIELDS,
        )
        return {
            "success": True,
            "duplicate": False,
            "record": normalized,
        }

    @staticmethod
    def _match_scalar_or_collection(actual: str, expected: Any) -> bool:
        if isinstance(expected, (list, tuple, set)):
            allowed = {str(item).strip() for item in expected}
            return str(actual).strip() in allowed
        return str(actual).strip() == str(expected).strip()

    def _match_filters(self, row, filters):
        if not filters:
            return True

        timestamp_from = filters.get("timestamp_from")
        timestamp_to = filters.get("timestamp_to")
        row_timestamp = row.get("timestamp", "")

        if timestamp_from and row_timestamp and row_timestamp < str(timestamp_from):
            return False
        if timestamp_to and row_timestamp and row_timestamp > str(timestamp_to):
            return False

        for key, expected in filters.items():
            if key in {"timestamp_from", "timestamp_to"}:
                continue
            if key == "decision":
                actual_decision = self._canonicalize_decision(row.get("decision", ""))
                if isinstance(expected, (list, tuple, set)):
                    expected_set = {self._canonicalize_decision(item) for item in expected}
                    if actual_decision not in expected_set:
                        return False
                else:
                    if actual_decision != self._canonicalize_decision(expected):
                        return False
                continue
            if not self._match_scalar_or_collection(row.get(key, ""), expected):
                return False
        return True

    def list_feedback(self, filters=None):
        filters = filters or {}
        entries = self.file_service.read_csv(self.log_file)
        filtered = []
        for row in entries:
            normalized_row = dict(row)
            normalized_row["decision"] = self._canonicalize_decision(normalized_row.get("decision", ""))
            if self._match_filters(normalized_row, filters):
                filtered.append(normalized_row)
        return filtered

    def feedback_summary(self, filters=None):
        summary = {
            "total": 0,
            "by_decision": {},
            "by_reason_code": {},
            "by_source_tab": {},
        }
        entries = self.list_feedback(filters=filters)
        summary["total"] = len(entries)

        for row in entries:
            decision = row.get("decision", "unknown") or "unknown"
            reason_code = row.get("reason_code", "unknown") or "unknown"
            source_tab = row.get("source_tab", "unknown") or "unknown"
            model_version = row.get("model_version", "unknown") or "unknown"

            summary["by_decision"][decision] = summary["by_decision"].get(decision, 0) + 1
            summary["by_reason_code"][reason_code] = summary["by_reason_code"].get(reason_code, 0) + 1
            summary["by_source_tab"][source_tab] = summary["by_source_tab"].get(source_tab, 0) + 1
            summary.setdefault("by_model_version", {})
            summary["by_model_version"][model_version] = summary["by_model_version"].get(model_version, 0) + 1

        return summary

    def export_training_labels(self, filters=None):
        filters = filters or {}
        filters.setdefault("source_tab", "human_feedback")
        feedback_rows = self.list_feedback(filters=filters)

        labels = []
        seen_keys = set()
        skipped = {
            "ineligible_decision": 0,
            "missing_required": 0,
            "missing_label_value": 0,
            "duplicates": 0,
        }

        for row in feedback_rows:
            decision = (row.get("decision") or "").strip().lower()
            if decision not in self.TRAINING_ELIGIBLE_DECISIONS:
                skipped["ineligible_decision"] += 1
                continue

            required_for_training = ["package_id", "loan_package", "document_type", "field_name", "idempotency_key"]
            if any(not str(row.get(field, "")).strip() for field in required_for_training):
                skipped["missing_required"] += 1
                continue

            unique_id = row["idempotency_key"]
            if unique_id in seen_keys:
                skipped["duplicates"] += 1
                continue
            seen_keys.add(unique_id)

            label_value = (row.get("corrected_value") or "").strip() or (row.get("model_prediction") or "").strip()
            if not label_value:
                skipped["missing_label_value"] += 1
                continue

            labels.append(
                {
                    "idempotency_key": unique_id,
                    "package_id": row.get("package_id", ""),
                    "loan_package": row.get("loan_package", ""),
                    "document_type": row.get("document_type", ""),
                    "field_name": row.get("field_name", ""),
                    "label_value": label_value,
                    "model_prediction": row.get("model_prediction", ""),
                    "decision": decision,
                    "reason_code": row.get("reason_code", ""),
                    "reviewer": row.get("reviewer", ""),
                    "timestamp": row.get("timestamp", ""),
                    "model_version": row.get("model_version", ""),
                    "run_id": row.get("run_id", ""),
                    "source_tab": row.get("source_tab", ""),
                }
            )

        return {
            "dataset_version": datetime.now(UTC).isoformat(),
            "filters": filters,
            "total_input_rows": len(feedback_rows),
            "total_exported_labels": len(labels),
            "skipped": skipped,
            "labels": labels,
        }

    def log_feedback(self, user, feedback_type, details):
        legacy_payload = {
            "package_id": details.get("package_id") or details.get("loan_package") or "unknown_package",
            "loan_package": details.get("loan_package") or details.get("package_id") or "unknown_package",
            "document_type": details.get("document_type") or details.get("doc_type") or "unknown_document",
            "field_name": details.get("field_name") or "general",
            "model_prediction": details.get("model_prediction") or details.get("prediction") or "",
            "corrected_value": details.get("corrected_value") or details.get("corrected") or "",
            "decision": details.get("decision") or "approve",
            "reason_code": details.get("reason_code") or feedback_type or "legacy_feedback",
            "comment": details.get("comment") or "",
            "reviewer": user,
            "timestamp": details.get("timestamp") or datetime.now(UTC).isoformat(),
            "model_version": details.get("model_version") or "unknown",
            "run_id": details.get("run_id") or "unknown",
            "source_tab": details.get("source_tab") or "human_feedback",
        }
        return self.submit_feedback(legacy_payload)

    def get_feedback(self, filter_type=None):
        filters = {"reason_code": filter_type} if filter_type else None
        return self.list_feedback(filters=filters)

    def summarize_feedback(self):
        return self.feedback_summary()

def collect_feedback(document):
    # Human feedback logic stub
    return {'status': 'feedback_collected', 'feedback': 'Sample feedback'}
