"""
ExtractionOrchestrationService: Orchestrates ZIP processing, per-PDF extraction,
field validation inference, escalation decisions, interaction log writing, and
escalated PDF saving for the AI Governance Platform.
"""
import csv
import datetime
import io
import json
import os
import sys
import uuid
import zipfile

# Allow imports from the scripts directory
_SCRIPTS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
if _SCRIPTS_PATH not in sys.path:
    sys.path.insert(0, _SCRIPTS_PATH)

from ai_governance_platform.services.extraction_service import extract_and_validate

CONFIDENCE_THRESHOLD = 0.8
MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "models", "field_validation_rf_encoded_model.joblib")
)
MODEL_FEATURES = [
    "is_empty",
    "is_negative",
    "is_nonsensical",
    "is_out_of_range",
    "field_encoded",
    "doc_type_encoded",
]
AI_INTERACTIONS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "logs", "ai_interactions.csv")
)
AI_INTERACTIONS_FIELDNAMES = [
    "timestamp",
    "user_role",
    "loan_package",
    "prompt",
    "response",
    "response_time_ms",
    "confidence_score",
    "risk_level",
    "decision",
    "rule_triggered",
    "reason",
    "required_controls",
    "hil_action",
    "hil_reviewer",
]
SAMPLE_ZIPS_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "sample_zips")
)


class ExtractionOrchestrationService:
    """Orchestrates the full loan-document extraction pipeline."""

    # ── Helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def reset_interaction_log(path: str = AI_INTERACTIONS_PATH) -> None:
        """Truncate ai_interactions.csv and write a fresh header."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=AI_INTERACTIONS_FIELDNAMES)
            writer.writeheader()

    @staticmethod
    def _load_inference_fn():
        """Import and return (load_model_fn, predict_validity_fn) from scripts."""
        from predict_field_validation import load_model, predict_validity  # noqa: PLC0415
        return load_model, predict_validity

    @classmethod
    def _compute_field_confidences(cls, fields: dict, doc_type: str, model) -> dict:
        """Run predict_validity for every field and return {field: probability}."""
        _, predict_validity = cls._load_inference_fn()
        confidences = {}
        for field, value in fields.items():
            _pred, prob = predict_validity(model, MODEL_FEATURES, field, value, doc_type)
            confidences[field] = prob
        return confidences

    @staticmethod
    def _append_interaction_row(row: dict, path: str = AI_INTERACTIONS_PATH) -> None:
        with open(path, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=AI_INTERACTIONS_FIELDNAMES)
            writer.writerow(row)

    # ── Main pipeline ─────────────────────────────────────────────────────

    @classmethod
    def process_zip(
        cls,
        zip_bytes: bytes,
        *,
        ai_interactions_path: str = AI_INTERACTIONS_PATH,
        model_path: str = MODEL_PATH,
    ) -> dict:
        """
        Process a ZIP of PDFs end-to-end.

        Returns:
            {
              "loan_package": str,
              "pdf_output_dir": str,
              "summary": {pdf_name: extraction_result, ...},
            }
        """
        # Reset session interaction log
        cls.reset_interaction_log(ai_interactions_path)

        loan_package = str(uuid.uuid4())[:8]
        pdf_output_dir = os.path.join(SAMPLE_ZIPS_ROOT, loan_package)
        os.makedirs(pdf_output_dir, exist_ok=True)
        escalated_dir = os.path.join(SAMPLE_ZIPS_ROOT, "escalated")
        os.makedirs(escalated_dir, exist_ok=True)

        # Load model once
        load_model, _ = cls._load_inference_fn()
        model = load_model(model_path)

        summary = {}
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            pdf_files = [f for f in z.namelist() if f.lower().endswith(".pdf")]
            for pdf_name in pdf_files:
                pdf_bytes = z.read(pdf_name)
                result = extract_and_validate(pdf_bytes)

                # Inference + confidence scoring
                field_confidences = cls._compute_field_confidences(
                    result.get("fields", {}),
                    result.get("doc_type", "Unknown"),
                    model,
                )
                result["field_confidences"] = field_confidences

                # Escalation decision
                escalate_fields = [
                    field
                    for field, conf in field_confidences.items()
                    if isinstance(conf, float) and conf < CONFIDENCE_THRESHOLD
                ]
                escalate = bool(escalate_fields)

                # Append confidence errors to result errors list
                for field in escalate_fields:
                    conf = field_confidences[field]
                    error_msg = f"{field.replace('_', ' ')} below confidence threshold ({conf:.2f})"
                    result.setdefault("errors", []).append(error_msg)

                now = datetime.datetime.now().isoformat()

                if escalate:
                    for field in escalate_fields:
                        conf = field_confidences[field]
                        row = {
                            "timestamp": now,
                            "user_role": "system",
                            "loan_package": loan_package,
                            "prompt": pdf_name,
                            "response": json.dumps(result["fields"]),
                            "response_time_ms": "",
                            "confidence_score": f"{conf:.2f}",
                            "risk_level": "high",
                            "decision": "escalate",
                            "rule_triggered": "escalate",
                            "reason": f"{field.replace('_', ' ')} below confidence threshold ({conf:.2f})",
                            "required_controls": "",
                            "hil_action": "",
                            "hil_reviewer": "",
                        }
                        cls._append_interaction_row(row, ai_interactions_path)

                    # Save the escalated PDF for reviewer download
                    pdf_path = os.path.join(escalated_dir, f"{loan_package}_{pdf_name}")
                    with open(pdf_path, "wb") as f:
                        f.write(pdf_bytes)
                else:
                    float_confs = [c for c in field_confidences.values() if isinstance(c, float)]
                    avg_conf = sum(float_confs) / len(float_confs) if float_confs else 0.0
                    row = {
                        "timestamp": now,
                        "user_role": "system",
                        "loan_package": loan_package,
                        "prompt": pdf_name,
                        "response": json.dumps(result["fields"]),
                        "response_time_ms": "",
                        "confidence_score": f"{avg_conf:.2f}",
                        "risk_level": "low",
                        "decision": "approve",
                        "rule_triggered": "",
                        "reason": ", ".join(result.get("errors", [])),
                        "required_controls": "",
                        "hil_action": "",
                        "hil_reviewer": "",
                    }
                    cls._append_interaction_row(row, ai_interactions_path)

                summary[pdf_name] = result

        return {
            "loan_package": loan_package,
            "pdf_output_dir": pdf_output_dir,
            "summary": summary,
        }
