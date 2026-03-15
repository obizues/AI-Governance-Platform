"""
demo_retrain_with_feedback.py
─────────────────────────────
Closes the human-in-the-loop training cycle:

  1. Export human-verified labels from FeedbackService
  2. Convert them into training records (field, value, doc_type, valid)
  3. Augment the base training dataset (deduplication applied)
  4. Retrain the field-validation RandomForest on the augmented data
  5. Save the new model + encoder + augmented dataset + training manifest

Can be run directly:
    python scripts/demo_retrain_with_feedback.py

Or called from the Streamlit UI:
    from scripts.demo_retrain_with_feedback import retrain_with_feedback
    result = retrain_with_feedback()
"""

import json
import os
import sys
import re
import joblib
import pandas as pd
from datetime import datetime, UTC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import OrdinalEncoder

# ── Path setup ──────────────────────────────────────────────────────────────
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

from ai_governance_platform.services.feedback_service import FeedbackService

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_TRAINING_PATH = os.path.join(REPO_ROOT, "ai_governance_platform", "data", "field_validation_training_full.json")
AUGMENTED_TRAINING_PATH = os.path.join(REPO_ROOT, "ai_governance_platform", "data", "field_validation_training_augmented.json")
MODEL_DIR = os.path.join(REPO_ROOT, "ai_governance_platform", "models")
# This is the model file the extraction pipeline always loads — retraining overwrites it
ACTIVE_MODEL_PATH = os.path.join(MODEL_DIR, "field_validation_rf_encoded_model.joblib")
MANIFEST_PATH = os.path.join(REPO_ROOT, "ai_governance_platform", "logs", "retrain_manifest.json")


# ── Helpers ──────────────────────────────────────────────────────────────────
def _normalize_doc_type(raw: str) -> str:
    """Convert feedback document_type (snake_case) to training data format (Title Case)."""
    return raw.replace("_", " ").title()


def _is_negative(val):
    try:
        return float(str(val).replace("$", "").replace(",", "")) < 0
    except Exception:
        return 0


def _is_nonsensical(val):
    return int(
        bool(re.match(r"[^\w\s]", str(val)))
        or bool(re.match(r"[a-zA-Z]+", str(val))) and not str(val).replace(" ", "").isalnum()
    )


def _is_out_of_range(field, val):
    try:
        if field == "credit_score":
            v = int(val)
            return int(v < 300 or v > 850)
        if field == "tax_year":
            v = int(val)
            return int(v < 1900 or v > 2100)
        if field == "interest_rate":
            v = float(str(val).replace("%", ""))
            return int(v < 0 or v > 20)
        if field in ("loan_amount", "income", "appraised_value"):
            v = float(str(val).replace("$", "").replace(",", ""))
            return int(v < 0 or v > 1_000_000)
        return 0
    except Exception:
        return 0


def _build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Engineer features identical to train_field_validation_model.py."""
    df = df.copy()
    df["is_empty"] = df["value"].apply(lambda v: 1 if isinstance(v, str) and v.strip() == "" else 0)
    df["is_negative"] = df.apply(lambda r: _is_negative(r["value"]), axis=1)
    df["is_nonsensical"] = df.apply(lambda r: _is_nonsensical(r["value"]), axis=1)
    df["is_out_of_range"] = df.apply(lambda r: _is_out_of_range(r["field"], r["value"]), axis=1)
    return df


def _feedback_labels_to_training_records(labels: list) -> list:
    """
    Convert FeedbackService export labels to training records.

    Decision semantics:
      matches_document → the extracted value IS valid  (one positive record)
      does_not_match   → the extracted value IS NOT valid (negative record)
                         AND the corrected value IS valid (positive record)
      approve (legacy) → treated as matches_document
    """
    records = []
    for label in labels:
        field = (label.get("field_name") or "").strip()
        doc_type = _normalize_doc_type((label.get("document_type") or "").strip())
        label_value = (label.get("label_value") or "").strip()
        model_prediction = (label.get("model_prediction") or "").strip()
        decision = (label.get("decision") or "").strip().lower()

        if not field or not doc_type or not label_value:
            continue

        if decision in ("matches_document", "approve"):
            records.append({"field": field, "value": label_value, "doc_type": doc_type, "valid": True})

        elif decision == "does_not_match":
            # The correct value (from the document) is a valid example
            records.append({"field": field, "value": label_value, "doc_type": doc_type, "valid": True})
            # The model's wrong extraction is an invalid example (adds a negative training signal)
            if model_prediction and model_prediction != label_value:
                records.append({"field": field, "value": model_prediction, "doc_type": doc_type, "valid": False})

    return records


def _load_manifest_history() -> list:
    if not os.path.exists(MANIFEST_PATH):
        return []
    try:
        with open(MANIFEST_PATH, "r") as f:
            history = json.load(f)
        if isinstance(history, list):
            return history
        if isinstance(history, dict):
            return [history]
    except Exception:
        return []
    return []


def reset_active_model_to_baseline(reset_manifest: bool = False):
    """
    Rebuild and activate a baseline model from the original training dataset.

    Parameters
    ----------
    reset_manifest : bool
        When True, replaces retrain_manifest.json with only this baseline reset entry.
        When False (default), appends the baseline reset entry to existing history.
    """
    try:
        with open(BASE_TRAINING_PATH, "r") as f:
            base_data = json.load(f)

        df = _build_features(pd.DataFrame(base_data))
        encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
        df[["field_encoded", "doc_type_encoded"]] = encoder.fit_transform(df[["field", "doc_type"]])

        feature_cols = ["is_empty", "is_negative", "is_nonsensical", "is_out_of_range", "field_encoded", "doc_type_encoded"]
        X = df[feature_cols]
        y = df["valid"].astype(int)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)

        y_pred = clf.predict(X_test)
        report = classification_report(y_test, y_pred, output_dict=True)
        report_text = classification_report(y_test, y_pred)

        os.makedirs(MODEL_DIR, exist_ok=True)
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        backup_model_filename = f"field_validation_rf_v0_11_1_baseline_{timestamp}.joblib"
        backup_encoder_filename = f"field_validation_rf_v0_11_1_baseline_{timestamp}_encoder.joblib"
        backup_model_path = os.path.join(MODEL_DIR, backup_model_filename)
        backup_encoder_path = os.path.join(MODEL_DIR, backup_encoder_filename)

        joblib.dump(clf, ACTIVE_MODEL_PATH)
        joblib.dump(clf, backup_model_path)
        joblib.dump(encoder, backup_encoder_path)

        manifest_entry = {
            "retrained_at": datetime.now(UTC).isoformat(),
            "model_version": "v0.11.1",
            "model_file": backup_model_filename,
            "encoder_file": backup_encoder_filename,
            "base_records": len(base_data),
            "feedback_labels_exported": 0,
            "new_training_records_added": 0,
            "label_weight": 1,
            "weighted_records_added": 0,
            "skipped_duplicates": 0,
            "total_augmented_records": len(base_data),
            "test_set_accuracy": report.get("accuracy"),
            "invalid_recall": (report.get("0") or {}).get("recall"),
            "invalid_precision": (report.get("0") or {}).get("precision"),
            "valid_recall": (report.get("1") or {}).get("recall"),
            "valid_precision": (report.get("1") or {}).get("precision"),
            "macro_f1": (report.get("macro avg") or {}).get("f1-score"),
            "weighted_f1": (report.get("weighted avg") or {}).get("f1-score"),
            "classification_report": report_text,
            "filters_applied": {"source_tab": "human_feedback"},
            "reset_to_baseline": True,
        }

        os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
        history = [] if reset_manifest else _load_manifest_history()
        history.append(manifest_entry)
        with open(MANIFEST_PATH, "w") as f:
            json.dump(history, f, indent=2)

        return {
            "success": True,
            "model_version": "v0.11.1",
            "active_model_path": ACTIVE_MODEL_PATH,
            "backup_model_path": backup_model_path,
            "backup_encoder_path": backup_encoder_path,
            "manifest_path": MANIFEST_PATH,
            "metrics": report,
            "classification_report": report_text,
        }
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def _next_model_version(history: list, default_base: str = "v0.11.1") -> str:
    candidate = default_base
    if history:
        latest = history[-1]
        candidate = (latest.get("model_version") or default_base).strip() or default_base

    match = re.match(r"^v(\d+)\.(\d+)\.(\d+)$", candidate)
    if not match:
        return "v0.11.1"
    major, minor, patch = (int(match.group(1)), int(match.group(2)), int(match.group(3)))
    return f"v{major}.{minor}.{patch + 1}"


def retrain_with_feedback(
    filters=None,
    label_weight: int = 10,
    force_promote: bool = False,
    override_reviewer: str = "",
    override_reason: str = "",
):
    """
    Run the full feedback → augment → retrain cycle.

    Parameters
    ----------
    filters : dict, optional
        Passed to FeedbackService.export_training_labels() to scope
        which feedback records are included (e.g. by model_version, date range).
    label_weight : int, optional (default 10)
        How many times each human-verified label is replicated in the augmented
        training set.  Because the base dataset has ~437 records, a weight of 10
        gives each human label roughly 10× the effective vote of a base record,
        which is enough to shift confidence past the 0.8 threshold after a single
        feedback submission and retrain.

    Returns
    -------
    dict with keys:
        success, model_path, encoder_path, augmented_data_path,
        base_records, new_records, augmented_records,
        metrics, manifest_path, error (on failure)
    """
    try:
        history = _load_manifest_history()
        effective_filters = dict(filters or {})
        effective_filters.setdefault("source_tab", "human_feedback")

        # ── 1. Export human-verified labels ─────────────────────────────────
        service = FeedbackService()
        export = service.export_training_labels(filters=effective_filters)
        labels = export.get("labels", [])

        if not labels:
            return {
                "success": False,
                "error": "No eligible training labels found in feedback log. "
                         "Submit Human Feedback with 'Matches document' or 'Does not match' decisions first.",
                "export_summary": export,
            }

        # ── 2. Convert labels → training records ────────────────────────────
        new_records = _feedback_labels_to_training_records(labels)

        if not new_records:
            return {
                "success": False,
                "error": "Feedback labels could not be converted to training records. "
                         "Check that field_name, document_type, and label_value are populated.",
                "export_summary": export,
            }

        # ── 3. Load base training data ───────────────────────────────────────
        with open(BASE_TRAINING_PATH, "r") as f:
            base_data = json.load(f)

        # ── 4. Deduplicate new records against everything already in base ────
        # Include 'valid' in the key so human corrections that contradict
        # legacy labels (same field/value/doc_type but opposite validity)
        # are treated as meaningful new evidence instead of being skipped.
        existing_keys = {
            (r["field"], str(r["value"]).strip(), r["doc_type"], bool(r.get("valid")))
            for r in base_data
        }

        deduped_new = []
        skipped_dupes = 0
        for rec in new_records:
            key = (rec["field"], str(rec["value"]).strip(), rec["doc_type"], bool(rec.get("valid")))
            if key in existing_keys:
                skipped_dupes += 1
            else:
                deduped_new.append(rec)
                existing_keys.add(key)  # prevent intra-batch dupes too

        if not deduped_new:
            return {
                "success": False,
                "error": (
                    "No learnable new feedback records to apply. All exported labels are already represented "
                    "in the base training data. Submit additional or different Human Feedback before retraining."
                ),
                "export_summary": export,
                "base_records": len(base_data),
                "new_records": 0,
                "weighted_records": 0,
                "skipped_duplicates": skipped_dupes,
                "filters_applied": effective_filters,
            }

        # Replicate each human-verified label label_weight times so that a small
        # number of feedback submissions can meaningfully shift model confidence.
        weighted_new = deduped_new * max(1, int(label_weight))
        augmented_data = base_data + weighted_new

        # ── 5. Save augmented training dataset ──────────────────────────────
        with open(AUGMENTED_TRAINING_PATH, "w") as f:
            json.dump(augmented_data, f, indent=2)

        # ── 6. Build feature matrix ──────────────────────────────────────────
        df = _build_features(pd.DataFrame(augmented_data))

        encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
        df[["field_encoded", "doc_type_encoded"]] = encoder.fit_transform(df[["field", "doc_type"]])

        feature_cols = ["is_empty", "is_negative", "is_nonsensical", "is_out_of_range", "field_encoded", "doc_type_encoded"]
        X = df[feature_cols]
        y = df["valid"].astype(int)

        # ── 7. Train ─────────────────────────────────────────────────────────
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)

        y_pred = clf.predict(X_test)
        report = classification_report(y_test, y_pred, output_dict=True)
        report_text = classification_report(y_test, y_pred)

        # ── 7b. Regression gate before production deployment ────────────────
        previous = history[-1] if history else {}
        candidate_accuracy = float(report.get("accuracy") or 0)
        candidate_invalid_recall = float((report.get("0") or {}).get("recall") or 0)
        candidate_macro_f1 = float((report.get("macro avg") or {}).get("f1-score") or 0)

        previous_accuracy = float(previous.get("test_set_accuracy") or 0)
        previous_invalid_recall = float(previous.get("invalid_recall") or 0)
        previous_macro_f1 = float(previous.get("macro_f1") or 0)

        deltas = {
            "accuracy": candidate_accuracy - previous_accuracy,
            "invalid_recall": candidate_invalid_recall - previous_invalid_recall,
            "macro_f1": candidate_macro_f1 - previous_macro_f1,
        }
        regressed_metrics = [name for name, delta in deltas.items() if delta < 0]
        blocked_by_governance = bool(history) and bool(regressed_metrics) and not force_promote

        model_version = _next_model_version(history)

        if blocked_by_governance:
            return {
                "success": False,
                "blocked_by_governance": True,
                "error": "Retrained candidate regressed on one or more KPIs and is blocked from production deployment.",
                "model_version": model_version,
                "base_records": len(base_data),
                "new_records": len(deduped_new),
                "label_weight": label_weight,
                "weighted_records": len(weighted_new),
                "skipped_duplicates": skipped_dupes,
                "augmented_records": len(augmented_data),
                "metrics": report,
                "invalid_recall": candidate_invalid_recall,
                "valid_recall": float((report.get("1") or {}).get("recall") or 0),
                "macro_f1": candidate_macro_f1,
                "classification_report": report_text,
                "export_summary": export,
                "filters_applied": effective_filters,
                "regressed_metrics": regressed_metrics,
                "metric_deltas": deltas,
                "previous_metrics": {
                    "accuracy": previous_accuracy,
                    "invalid_recall": previous_invalid_recall,
                    "macro_f1": previous_macro_f1,
                },
                "candidate_metrics": {
                    "accuracy": candidate_accuracy,
                    "invalid_recall": candidate_invalid_recall,
                    "macro_f1": candidate_macro_f1,
                },
            }

        # ── 8. Save model + encoder ──────────────────────────────────────────
        os.makedirs(MODEL_DIR, exist_ok=True)
        model_version_token = model_version.replace(".", "_")
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        model_filename = f"field_validation_rf_{model_version_token}_{timestamp}.joblib"
        encoder_filename = f"field_validation_rf_{model_version_token}_{timestamp}_encoder.joblib"
        model_path = os.path.join(MODEL_DIR, model_filename)
        encoder_path = os.path.join(MODEL_DIR, encoder_filename)

        joblib.dump(clf, model_path)
        joblib.dump(encoder, encoder_path)

        # Also overwrite the active model so the extraction pipeline
        # immediately picks up the retrained version on next prediction.
        joblib.dump(clf, ACTIVE_MODEL_PATH)

        # ── 9. Write manifest ────────────────────────────────────────────────
        manifest = {
            "retrained_at": datetime.now(UTC).isoformat(),
            "model_version": model_version,
            "model_file": model_filename,
            "encoder_file": encoder_filename,
            "base_records": len(base_data),
            "feedback_labels_exported": export.get("total_exported_labels", 0),
            "new_training_records_added": len(deduped_new),
            "label_weight": label_weight,
            "weighted_records_added": len(weighted_new),
            "skipped_duplicates": skipped_dupes,
            "total_augmented_records": len(augmented_data),
            "test_set_accuracy": report.get("accuracy"),
            "invalid_recall": (report.get("0") or {}).get("recall"),
            "invalid_precision": (report.get("0") or {}).get("precision"),
            "valid_recall": (report.get("1") or {}).get("recall"),
            "valid_precision": (report.get("1") or {}).get("precision"),
            "macro_f1": (report.get("macro avg") or {}).get("f1-score"),
            "weighted_f1": (report.get("weighted avg") or {}).get("f1-score"),
            "classification_report": report_text,
            "filters_applied": effective_filters,
            "force_promoted": bool(force_promote),
            "force_promoted_by": str(override_reviewer or "").strip(),
            "force_promoted_reason": str(override_reason or "").strip(),
            "metric_deltas_vs_previous": deltas,
            "regressed_metrics_vs_previous": regressed_metrics,
        }

        os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
        # Append to manifest log (keep history of all retrain runs)
        history.append(manifest)
        with open(MANIFEST_PATH, "w") as f:
            json.dump(history, f, indent=2)

        return {
            "success": True,
            "model_path": model_path,
            "encoder_path": encoder_path,
            "augmented_data_path": AUGMENTED_TRAINING_PATH,
            "manifest_path": MANIFEST_PATH,
            "model_version": model_version,
            "base_records": len(base_data),
            "new_records": len(deduped_new),
            "label_weight": label_weight,
            "weighted_records": len(weighted_new),
            "skipped_duplicates": skipped_dupes,
            "augmented_records": len(augmented_data),
            "metrics": report,
            "invalid_recall": (report.get("0") or {}).get("recall"),
            "valid_recall": (report.get("1") or {}).get("recall"),
            "macro_f1": (report.get("macro avg") or {}).get("f1-score"),
            "classification_report": report_text,
            "export_summary": export,
            "filters_applied": effective_filters,
        }

    except Exception as exc:
        return {"success": False, "error": str(exc)}


# ── CLI entry point ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Retraining field validation model with human feedback")
    print("=" * 60)

    result = retrain_with_feedback()

    if not result["success"]:
        print(f"\n[FAILED] {result['error']}")
        sys.exit(1)

    print(f"\n✓ New model version:        {result['model_version']}")
    print(f"✓ Base training records:   {result['base_records']}")
    print(f"✓ Unique new records:        {result['new_records']} ({result['skipped_duplicates']} duplicates skipped)")
    print(f"✓ Label weight:              {result['label_weight']}×  →  {result['weighted_records']} weighted records added")
    print(f"✓ Augmented dataset total:   {result['augmented_records']} records")
    print(f"\n✓ Active model overwritten:  {ACTIVE_MODEL_PATH}")
    print(f"✓ Timestamped backup:        {result['model_path']}")
    print(f"✓ Encoder backup:            {result['encoder_path']}")
    print(f"✓ Manifest:                  {result['manifest_path']}")
    print(f"\n── Classification Report ──────────────────────────────────")
    print(result["classification_report"])
