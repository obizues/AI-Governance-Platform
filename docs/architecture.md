# AI Governance & Evaluation Platform Architecture

## Version: v1.0.0

## Architectural intent

This platform demonstrates an AI-native governed document-intelligence loop where:

1. LLM extraction (or hybrid extraction) produces structured fields,
2. low-confidence results are escalated,
3. human reviewers make operational decisions,
4. separate human training labels are collected,
5. only training-eligible labels flow into retraining,
6. retrained models are versioned, monitored, and auditable.

---

## Primary tabs and responsibilities

- **Extract & Validate** — document upload, AI-native extraction, confidence scoring, escalation triggering
- **Escalation Decisions** — operational HIL review (`approve` / `deny`)
- **Human Training Labels** — source-of-truth labels (`matches_document`, `does_not_match`, `cannot_verify`)
- **Model Monitoring** — pending labels, retrain controls, model version KPIs, baseline reset
- **Governance & Audit** — human label history and escalation decision history

---

## Component diagram

```mermaid
graph TD
  User --> StreamlitUI
  StreamlitUI --> ExtractionService
  StreamlitUI --> LLMStatus[LLM Runtime Status Card]
  LLMStatus --> LLMExtractionService
  StreamlitUI --> EscalationService
  StreamlitUI --> FeedbackService
  StreamlitUI --> EvaluationService
  StreamlitUI --> MetricsService
  ExtractionService --> LLMExtractionService
  LLMExtractionService --> Ollama[Ollama / OpenAI-Compatible Provider]
  ExtractionService --> Models
  ExtractionService --> Data
  ExtractionService --> Logs
  EscalationService --> Logs
  FeedbackService --> Logs
  MetricsService --> Logs
  RetrainScript[demo_retrain_with_feedback.py] --> FeedbackService
  RetrainScript --> Data
  RetrainScript --> Models
  RetrainScript --> Logs
  Logs --> GovernanceAudit[Governance & Audit Views]
  Models --> StreamlitUI
```

---

## Human-in-the-loop flow

```mermaid
flowchart LR
  A[Upload ZIP of PDFs] --> B[Extract fields]
  B --> B1{Extraction mode}
  B1 -->|rules| B2[Deterministic parser]
  B1 -->|llm| B3[LLM extractor]
  B1 -->|hybrid| B4[Rules + LLM enrichment]
  B3 --> B5{LLM available?}
  B5 -- No --> B2
  B5 -- Yes --> C[Score field confidence]
  B2 --> C
  B4 --> C
  C --> D{Confidence < 0.80?}
  D -- No --> E[Return validated extraction]
  D -- Yes --> F[Escalate field]
  F --> G[Escalation Decisions tab]
  G --> H{Approve or Deny operational use?}
  H --> I[Governance log]
  F --> J[Human Training Labels tab]
  J --> K{Matches / Does not match / Cannot verify}
  K --> L[Training-eligible label export]
  L --> M[Retrain model]
  M --> N[Versioned model + active model overwrite]
  N --> O[Re-run extraction under newer model version]
```

---

## Retraining flow

```mermaid
sequenceDiagram
  participant Reviewer
  participant UI as Streamlit UI
  participant FB as FeedbackService
  participant RT as Retrain Script
  participant M as Models Directory
  participant Mon as Monitoring UI

  Reviewer->>UI: Submit human training label
  UI->>FB: submit_feedback(..., source_tab='human_feedback')
  Reviewer->>UI: Click Retrain with Human Feedback
  UI->>RT: retrain_with_feedback(label_weight=n)
  RT->>FB: export_training_labels(source_tab='human_feedback')
  RT->>RT: build learnable records + apply weighting
  RT->>M: save versioned backup model
  RT->>M: overwrite active model file
  RT->>Mon: append manifest entry with KPIs
  Reviewer->>UI: Re-run extraction
  UI->>M: load active model
```

---

## Key logs and artifacts

- `logs/ai_interactions.csv` — extraction and escalation interaction log
- `logs/hil_actions.csv` — escalation review action log
- `logs/feedback_log.csv` — structured human feedback and training labels
- `logs/retrain_manifest.json` — model version history and KPI history
- `models/field_validation_rf_encoded_model.joblib` — active deployed model
- `models/field_validation_rf_v*_*.joblib` — versioned model backups
- LLM runtime is provider-backed (local Ollama by default in launcher) with status surfaced in UI

---

## KPI philosophy

Primary KPIs:

- **Invalid Recall** — are bad extractions being caught?
- **Macro F1** — is class balance improving or degrading?
- **Escalation Review Rate** — are governance decisions being completed?
- **Pending Label Ratio** — is human feedback waiting to be learned from?

Retrain results are labeled as `Improved`, `Mixed`, `Regressed`, or `Baseline` to avoid overclaiming success.

---

## Demo reset capability

The app includes a baseline reset to restore the active model to **v0.11.1 baseline** so the before/after HIL demo can be replayed reliably.