
## [v0.9.1] - 2026-03-10
### Updates
- Version bump to v0.9.1
- Audit log and escalation CSV parsing fixes
- UI error message standardization
- Documentation and README updates
- Requirements.txt reviewed

# [v0.9.0] - 2026-03-10
### Major Updates
- Modularized all business logic into service modules
- Centralized config, data, and logs folders
- Refactored app.py to use service modules
- Removed legacy and duplicate files/folders
- Cleaned up project structure for maintainability
- Updated documentation and tests
- Demo Files sidebar expander with download buttons
- Dynamic listing of sample_zips files
- Streamlit download buttons for demo files
- Improved sidebar layout and UI/UX
- Real-time escalation review and human-in-the-loop workflow
- Modular audit logging, policy engine, feedback, and metrics
- All documentation and sidebar content up to date

# [v0.4.0] - 2026-03-08
# [v0.5.0] - 2026-03-08
### Major Updates
- Real-time escalation review count updates after query submission
- Prompt/session state fixes for accurate query context
- CSV audit log flush for immediate sync
- UI bug fixes for escalation navigation and count
- Robust escalation workflow and audit logging

# Changelog

## [v0.5.0] - 2026-03-08
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
### Major Updates