"""
ModelMonitoringService: Handles retrain manifest reading, metric extraction,
outcome classification, and KPI trend computations for the AI Governance Platform.
"""
import json
import os
import re

MANIFEST_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "logs", "retrain_manifest.json")
)
BASELINE_MODEL_VERSION = "v0.11.1"


class ModelMonitoringService:
    # ── Metric parsing ────────────────────────────────────────────────────

    @staticmethod
    def extract_report_metric(report_text: str, label: str, metric_name: str):
        """Parse a single metric value from a sklearn classification report string."""
        if not report_text:
            return None
        lines = str(report_text).splitlines()
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            tokens = stripped.split()
            if label == "macro avg":
                if len(tokens) >= 5 and tokens[0] == "macro" and tokens[1] == "avg":
                    mapping = {"precision": 2, "recall": 3, "f1-score": 4}
                    idx = mapping.get(metric_name)
                    if idx is not None:
                        try:
                            return float(tokens[idx])
                        except Exception:
                            return None
            else:
                if len(tokens) >= 5 and tokens[0] == label:
                    mapping = {"precision": 1, "recall": 2, "f1-score": 3}
                    idx = mapping.get(metric_name)
                    if idx is not None:
                        try:
                            return float(tokens[idx])
                        except Exception:
                            return None
        return None

    # ── Version helpers ───────────────────────────────────────────────────

    @staticmethod
    def parse_semver(version: str):
        """Return (major, minor, patch) tuple or None."""
        match = re.match(r"^v(\d+)\.(\d+)\.(\d+)$", str(version or "").strip())
        if not match:
            return None
        return tuple(int(match.group(i)) for i in range(1, 4))

    @classmethod
    def is_older_version(cls, version: str, reference: str) -> bool:
        parsed_version = cls.parse_semver(version)
        parsed_reference = cls.parse_semver(reference)
        if not parsed_version or not parsed_reference:
            return False
        return parsed_version < parsed_reference

    # ── Manifest access ───────────────────────────────────────────────────

    @staticmethod
    def load_manifest(manifest_path: str = MANIFEST_PATH):
        """Load and return the retrain manifest list. Returns [] on any error."""
        if not os.path.exists(manifest_path):
            return []
        try:
            with open(manifest_path) as f:
                history = json.load(f)
            return history if isinstance(history, list) else []
        except Exception:
            return []

    @classmethod
    def enrich_history(cls, history: list) -> list:
        """Fill missing recall/precision/f1 fields from classification_report text."""
        for run in history:
            report = run.get("classification_report", "")
            if run.get("invalid_recall") is None:
                run["invalid_recall"] = cls.extract_report_metric(report, "0", "recall")
            if run.get("invalid_precision") is None:
                run["invalid_precision"] = cls.extract_report_metric(report, "0", "precision")
            if run.get("valid_recall") is None:
                run["valid_recall"] = cls.extract_report_metric(report, "1", "recall")
            if run.get("valid_precision") is None:
                run["valid_precision"] = cls.extract_report_metric(report, "1", "precision")
            if run.get("macro_f1") is None:
                run["macro_f1"] = cls.extract_report_metric(report, "macro avg", "f1-score")
        return history

    # ── Active model badge metadata ───────────────────────────────────────

    @classmethod
    def load_active_model_metadata(cls, manifest_path: str = MANIFEST_PATH) -> dict:
        """Return display metadata for the active model badge in the sidebar."""
        metadata = {
            "version": BASELINE_MODEL_VERSION,
            "label": "field_validation_rf_encoded_model.joblib (baseline deployment)",
            "color": "#e3f2fd",
            "border": "#90caf9",
            "text": "#0d47a1",
        }

        history = cls.load_manifest(manifest_path)
        if not history:
            return metadata

        latest = history[-1] or {}
        latest_version = str(latest.get("model_version") or BASELINE_MODEL_VERSION).strip() or BASELINE_MODEL_VERSION
        latest_model_file = str(
            latest.get("model_file") or "field_validation_rf_encoded_model.joblib"
        ).strip() or "field_validation_rf_encoded_model.joblib"
        latest_date = str(latest.get("retrained_at") or "").strip()[:10]
        reset_to_baseline = bool(latest.get("reset_to_baseline"))

        if reset_to_baseline:
            status_text = f"baseline reset {latest_date}" if latest_date else "baseline reset"
        else:
            status_text = f"feedback-retrained {latest_date}" if latest_date else "feedback-retrained"

        if reset_to_baseline and cls.is_older_version(latest_version, BASELINE_MODEL_VERSION):
            status_text = f"legacy baseline reset {latest_date}" if latest_date else "legacy baseline reset"

        metadata.update(
            {
                "version": latest_version,
                "label": f"{latest_version} | {latest_model_file} ({status_text})",
                "color": "#f6fff8",
                "border": "#b7e4c7",
                "text": "#1b5e20",
            }
        )
        return metadata

    # ── Retrain outcome classification ────────────────────────────────────

    @staticmethod
    def retrain_outcome(current_run: dict, previous_run: dict = None) -> tuple:
        """
        Returns (label, text_color, bg_color, reason_text).
        label is one of: Baseline | Improved | Regressed | Mixed
        """
        if not previous_run:
            return ("Baseline", "#0d47a1", "#e3f2fd", "First tracked model in history")

        acc_delta = float(current_run.get("test_set_accuracy") or 0) - float(
            previous_run.get("test_set_accuracy") or 0
        )
        invalid_recall_delta = float(current_run.get("invalid_recall") or 0) - float(
            previous_run.get("invalid_recall") or 0
        )
        macro_f1_delta = float(current_run.get("macro_f1") or 0) - float(
            previous_run.get("macro_f1") or 0
        )

        if invalid_recall_delta >= 0 and macro_f1_delta >= 0 and acc_delta >= 0:
            return ("Improved", "#1b5e20", "#f6fff8", "Safety and overall balance improved or held")
        if invalid_recall_delta < 0 and macro_f1_delta < 0:
            return ("Regressed", "#b71c1c", "#ffebee", "Caught fewer invalid cases and overall balance got worse")
        return ("Mixed", "#8d6e00", "#fff8e1", "Some metrics improved while others declined")

    # ── Trend data ────────────────────────────────────────────────────────

    @classmethod
    def build_trend_dataframe(cls, history: list) -> list:
        """Return a list of dicts suitable for a pandas DataFrame trend chart."""
        rows = []
        for idx, run in enumerate(history, start=1):
            prev_run = history[idx - 2] if idx > 1 else None
            run_outcome, _, _, _ = cls.retrain_outcome(run, prev_run)
            rows.append(
                {
                    "run": idx,
                    "model_version": run.get("model_version", f"run-{idx}"),
                    "outcome": run_outcome,
                    "retrained_at": run.get("retrained_at", ""),
                    "model_file": run.get("model_file", ""),
                    "accuracy": round(float(run.get("test_set_accuracy", 0) or 0) * 100, 2),
                    "invalid_recall": round(float(run.get("invalid_recall", 0) or 0) * 100, 2),
                    "macro_f1": round(float(run.get("macro_f1", 0) or 0) * 100, 2),
                    "new_records": int(run.get("new_training_records_added", 0) or 0),
                    "weighted_records": int(run.get("weighted_records_added", 0) or 0),
                    "label_weight": int(run.get("label_weight", 1) or 1),
                }
            )
        return rows

    # ── Pending label filter ──────────────────────────────────────────────

    @classmethod
    def get_pending_label_filters(cls, manifest_path: str = MANIFEST_PATH) -> dict:
        """Return a feedback filter dict with timestamp_from = last retrain time."""
        filters = {"source_tab": "human_feedback"}
        history = cls.load_manifest(manifest_path)
        if history:
            last_retrained_at = str(history[-1].get("retrained_at", "")).strip()
            if last_retrained_at:
                filters["timestamp_from"] = last_retrained_at
        return filters
