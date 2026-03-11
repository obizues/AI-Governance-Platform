
## 🤖 AI Governance & Evaluation Platform v0.9.1

📝 Audit Logging for all AI interactions
⚖️ Policy Engine for query risk assessment
💬 Feedback logging and summary
🛑 Escalation Review & Human-in-the-Loop (HIL) for low-confidence or high-risk documents
📊 System Health KPIs and metrics
📄 Document Extraction, Validation, and Confidence Scoring
🗂️ Audit Log Tab & Sequential Loan Numbering
🖥️ Streamlit-based modern UI
🌐 Open-source, modular Python codebase

---

## About this project
This platform enables safe, observable, and governed AI operations for enterprise environments. It features modular business logic, real-time escalation review, document extraction and validation, audit logging, feedback collection, and system health metrics. Designed for CTOs, CEOs, hiring managers, and PE operators.

## Project Documentation
- docs/README.md: Documentation folder purpose
- docs/architecture.md: System architecture and flow diagrams
- docs/CHANGELOG.md: Release notes and updates
- README.md: Project overview, setup, features

## Tech Stack
- Python 3.10+
- Streamlit (UI)
- pandas, pdfplumber (data extraction)
- Modular service architecture
- YAML for policy configuration
- Pytest for testing

## System Design Notes
- All business logic is modularized in services/
- Centralized config/, data/, and logs/ folders
- UI is decoupled from core logic
- Policy rules in config/policy.yaml
- Feedback loop via services/feedback_service.py
- KPIs and metrics via services/metrics_service.py

---
```
ai_governance_platform/
   services/        # Modular business logic (extraction, validation, audit logging, feedback, file management, metrics, policy, provider)
   config/          # Centralized configuration files (policy.yaml, document_types.py)
   data/            # Evaluation datasets, reports, summaries
   logs/            # Audit and feedback logs
   ui/              # Streamlit app (with banners, sidebar, tabs)
   tests/           # Pytest tests
docs/              # Project documentation (architecture, changelog, etc.)
main.py            # CLI runner
README.md          # Project documentation
requirements.txt   # Python dependencies
```

## Quickstart
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Version: v0.9.1
2. Run CLI demo:
   ```sh
   python ai_governance_platform/main.py
   ```
3. Run Streamlit UI:
   ```sh
   streamlit run ai_governance_platform/ui/app.py
   ```

## Governance Logic
- All core logic is UI-agnostic and modular, implemented in service modules.
- Policy rules are defined in `config/policy.yaml`.
- Feedback loop aggregates feedback and escalates problematic prompts via `services/feedback_service.py`.

## Evaluation
- Automated evaluation uses `data/evaluation_dataset.json` and outputs `data/evaluation_report.json`.
- **Known Bug:** Running evaluation may result in a `FileNotFoundError` if the dataset file is missing. Ensure `data/evaluation_dataset.json` exists.

## System Health
- KPIs: total queries, deny rate, escalation rate, avg latency, positive feedback rate, trust score.
- **Known Bug:** System Health tab may not display metrics correctly if log files are missing or malformed.

## Documentation & Links
- 🌐 [GitHub Repository](https://github.com/obizues/AI-Governance-Platform)
- 📘 [README.md](https://github.com/obizues/AI-Governance-Platform/blob/main/README.md): Platform overview, setup, features
- 📝 [CHANGELOG.md](https://github.com/obizues/AI-Governance-Platform/blob/main/CHANGELOG.md): Release notes and updates
- 🗂️ [System Architecture](https://github.com/obizues/AI-Governance-Platform/blob/main/docs/architecture.md): Design and flow diagrams

## Contributing
- Fork, branch, and submit PRs.
- See CHANGELOG.md for release history.

## v0.5.0 Updates

### Added
- Real-time escalation review count updates after query submission
- Prompt/session state fixes for accurate query context
- CSV audit log flush for immediate sync
- UI bug fixes for escalation navigation and count
- Robust escalation workflow and audit logging

### Changed
- Escalation review logic now guarantees immediate visibility of escalated queries
- Audit logger flushes CSV after every write
- Session state always uses prompt at button press

### Fixed
- Escalation count not updating on first query
- Session state mismatches for prompt/response
- TypeError in escalation navigation
- UI/UX improvements for Live Query tab, banners, sidebar, and documentation links
- Info messages now reliably show when no query is present or after feedback
- Feedback submission and cleanup logic improved
- Indentation, import, and session state bugs fixed
- Audit logging refactored to avoid shadowing standard library
- All __init__.py files added for package structure
- Evaluation and KPI logic clarified in documentation
