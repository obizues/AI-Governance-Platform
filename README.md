
# AI Governance & Evaluation Platform 🤖
**Version:** v0.8.0
A modular, open-source platform for safe, observable, and governed AI operations in enterprise environments.
- Real-time escalation sync and human review workflow
- Document extraction, validation, and confidence scoring
- Audit log tab with full review history
- Sequential loan numbering and improved UI/UX
- Feedback logging and summary for continuous improvement
- System Health KPIs for operational visibility
- Streamlit-based modern UI for business users
- Open-source, extensible Python codebase
- Demo Files sidebar expander with download buttons
- Dynamic listing of sample_zips files
- Streamlit download buttons for demo files
- Improved sidebar layout and UI/UX
- Designed for CTOs, CEOs, hiring managers, and PE operators
```
/ai_governance_platform
  /app            # Entrypoints / minimal UI hooks
  /audit_logging  # Audit logger (renamed from /logging)
  /evaluation     # Dataset, runner, scoring, report
  /feedback       # Feedback logging & summary
  /policy         # policy.yaml, policy engine, feedback gate
  /providers      # AI provider interface + stub provider
  /metrics        # KPI calculations
  /ui             # Streamlit app (with banners, sidebar, tabs)
  /tests          # Pytest tests
main.py           # CLI runner
README.md         # Project documentation
CHANGELOG.md      # Release notes
requirements.txt  # Python dependencies
/logs             # Audit and feedback logs
```

## Quickstart
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Run CLI demo:
   ```sh
   python ai_governance_platform/main.py
   ```
3. Run Streamlit UI:
   ```sh
   streamlit run ai_governance_platform/ui/app.py
   ```

## Governance Logic
- All core logic is UI-agnostic and modular.
- Policy rules are defined in `policy/policy.yaml`.
- Feedback loop aggregates feedback and escalates problematic prompts.

## Evaluation
- Automated evaluation uses `evaluation/evaluation_dataset.json` and outputs `evaluation/evaluation_report.json`.
- **Known Bug:** Running evaluation may result in a `FileNotFoundError` if the dataset file is missing. Ensure `evaluation/evaluation_dataset.json` exists.

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
