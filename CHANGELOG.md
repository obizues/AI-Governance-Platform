# [v0.4.0] - 2026-03-08
### Major Updates
- Escalation workflow reliably updates CSV and removes reviewed escalations from UI
- Mask logic in escalation.py now matches only by timestamp for robust row updates
- All documentation, sidebar, and app version references updated to v0.4.0

# Changelog

## [v0.1.0] - 2026-03-04
- Initial proof-of-concept release
- Modular architecture
- Audit logging, policy engine, evaluation, feedback, Streamlit UI
- Feedback loop and escalation logic
- KPI metrics and system health tab
- Documentation updated for public release
- Known bugs:
	- Evaluation may fail with FileNotFoundError if dataset is missing
	- System Health tab may not display metrics correctly

## [v0.2.0] - 2026-03-04
- Major UI/UX improvements for Live Query tab
- Info messages now reliably show when no query is present or after feedback
- Feedback submission and cleanup logic improved
- Indentation, import, and session state bugs fixed
- Audit logging refactored to avoid shadowing standard library
- All __init__.py files added for package structure
- Evaluation and KPI logic clarified in documentation
- Known bugs:
    - System Health tab may not display metrics correctly if log files are missing or malformed
    - Evaluation may fail with FileNotFoundError if dataset is missing

## [v0.3.0] - 2026-03-08
### Major Updates
- Modernized UI with collapsible sidebar, emoji icons, and top banner
- Updated documentation: README, requirements, architecture
- Added docs/architecture.md with component diagram and extensibility notes
- Improved audit logging, feedback, evaluation, and metrics modules
- Enhanced links and sidebar content for clarity
- Version bump and GitHub tagging for v0.3.0
