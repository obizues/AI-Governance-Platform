# 🤖 AI Governance & Evaluation Platform v1.1.0

An AI-native enterprise governance platform for document intelligence with:

- LLM-native document extraction (local Ollama or OpenAI-compatible providers)
- field-level confidence scoring and deterministic safety validation
- escalation decisions for low-confidence or risky outputs
- human training labels for supervised feedback
- governed retraining with model versioning
- KPI monitoring that prioritizes safety and balance, not just accuracy
- audit and governance history for reviewers and model changes

---

## What this app demonstrates

The app now supports a full human-in-the-loop loop:

1. **Extract & Validate** — upload a ZIP of PDFs, extract fields, score field confidence, and escalate low-confidence outputs.
2. **Escalation Decisions** — reviewers decide whether an escalated extraction can proceed operationally.
3. **Human Training Labels** — reviewers compare model output to the source document and submit ground-truth labels.
4. **Model Monitoring** — pending labels, retrain controls, model version history, and KPI trends.
5. **Governance & Audit** — full human feedback history plus escalation decision history.

This enables a realistic demo of:

- a bad/low-confidence extraction being escalated,
- a human reviewer confirming the true value,
- retraining the model with governed feedback,
- re-running the same package under a newer model version,
- and observing whether the issue is no longer escalated.

---

## Version

Current application version: **v1.1.0**

Baseline model version for demo reset: **v0.11.1**

---

## Core capabilities in v1.1.0

- **AI-native extraction runtime** with configurable `rules` / `llm` / `hybrid` modes
- **Local-first LLM operation** via Ollama, with OpenAI-compatible provider support
- **Live LLM status visibility** in the UI (mode, provider, model, runtime health)
- **Field-level confidence scoring** with escalation threshold visibility in the UI
- **Operational HIL decisions** separated from **training labels**
- **Training-eligible label export** limited to known-ground-truth human feedback
- **Retraining with model versioning** and active model overwrite for immediate use in extraction
- **Pre-production retrain guardrail** that blocks candidate deployment on KPI regression unless Force Promote is explicitly approved
- **Baseline reset** to replay the before/after demo loop
- **KPI monitoring** focused on:
  - invalid recall
  - macro F1
  - escalation review rate
  - pending training label ratio
- **Governance visibility** for both:
  - escalation review history
  - human training label history

---

## Project structure

```text
ai_governance_platform/
  config/           # Policy and document-type configuration
  data/             # Training data, evaluation data, generated reports
  logs/             # Feedback logs, HIL logs, training manifest, KPIs
  models/           # Active model + timestamped versioned backups
  services/         # Extraction, escalation, feedback, policy, metrics, file services
  tests/            # Service-level tests
  ui/               # Streamlit application
docs/               # Architecture and release documentation
scripts/            # Training, retraining, prediction utilities
README.md           # Product overview and setup
requirements.txt    # Python dependencies
```

---

## Quickstart

1. Install dependencies

   ```sh
   pip install -r requirements.txt
   ```

2. Launch the app

   ```sh
   python launcher.py
   ```

   or

   ```sh
   streamlit run ai_governance_platform/ui/app.py
   ```

3. Demo the loop

   - Reset to baseline model in **Model Monitoring**
   - Upload a package in **Extract & Validate**
   - Review the escalated issue in **Escalation Decisions**
   - Submit a source-document label in **Human Training Labels**
   - Retrain the model in **Model Monitoring**
   - Re-run extraction and compare the outcome under the new model version

---

## LLM extraction modes

The app supports three extraction modes:

- `rules` — deterministic parser only
- `llm` — LLM-only extraction
- `hybrid` — deterministic parser + LLM enrichment

Set environment variables before launching the app:

```sh
# options: rules | llm | hybrid
set AI_EXTRACTION_MODE=hybrid

# provider: openai (cloud) or ollama (local)
set LLM_PROVIDER=openai
set LLM_MODEL=gpt-4o-mini
set OPENAI_API_KEY=YOUR_KEY_HERE
```

For local Ollama instead:

```sh
set AI_EXTRACTION_MODE=hybrid
set LLM_PROVIDER=ollama
set LLM_MODEL=llama3.2
set OLLAMA_BASE_URL=http://localhost:11434/v1
```

Mode behavior:

- `rules`: existing parser only
- `llm`: LLM-only extraction
- `hybrid`: rules first, then LLM enriches/overrides non-empty fields

If LLM inference fails, extraction falls back safely to deterministic rules.

---

## KPI interpretation

- **Invalid Recall**: higher is better; measures how many truly bad values are caught
- **Macro F1**: higher is better; balances valid and invalid classes
- **Accuracy**: useful, but not sufficient on its own
- **Pending Label Ratio**: operational KPI showing how much new human feedback is still waiting to be learned from

The app intentionally distinguishes:

- **local improvement** on a targeted use case
- from **global model quality** across all patterns

That is why retrain outcomes are labeled as **Improved**, **Mixed**, or **Regressed** rather than assuming all retrains are beneficial.

Additionally, retrain promotion is governance-gated: if the candidate regresses against current production KPIs, deployment is blocked by default and requires explicit **Force Promote** approval with reviewer accountability and written justification.

---

## Documentation

- [docs/README.md](docs/README.md) — documentation index
- [docs/architecture.md](docs/architecture.md) — architecture, flow, and diagrams
- [docs/CHANGELOG.md](docs/CHANGELOG.md) — release history
- [docs/CHANGELOG-v1.1.0.md](docs/CHANGELOG-v1.1.0.md) — v1.1.0 release notes

---

## Why this is a strong HIL governance demo

This app now demonstrates the full governance pattern:

- AI output is observable
- risky/low-confidence output is escalated
- humans make operational decisions separately from training labels
- only eligible labels flow into retraining
- retrained models are versioned and monitored
- broader safety/performance KPIs can prevent overclaiming improvement

That makes it a credible demo of AI oversight, human feedback, and controlled accuracy improvement.
