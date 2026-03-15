# Changelog

## [v0.11.1] - 2026-03-15

### Changed
- Sidebar "About This Project" copy rewritten to match final HIL + retraining workflow tone
- Sidebar "Tech Stack" updated to list all actual stack components (scikit-learn, joblib, pdfplumber, etc.)
- Sidebar "System Design Notes" updated to describe actual architectural choices for governance separation, manifest-driven retraining, and baseline reset
- Sidebar summary bullets updated to drop legacy wording (Audit Log Tab, System Health KPIs, Sequential Loan Numbering)

### Fixed
- Active model sidebar badge now correctly labels baseline resets (vs feedback retrains) and avoids showing legacy v0.10.0 metadata after a v0.11.0 upgrade
- Governance & Audit tab escalation history now reads persistent structured escalation-review records from `feedback_log.csv` instead of the session-only interaction log (which was reset on each new upload)
- Pending escalation count in the Governance tab now reflects the current interaction log state separately from the governance history rows

## [v0.11.0] - 2026-03-15

### Added
- Separation between **Escalation Decisions** and **Human Training Labels**
- Governed retraining with active-model overwrite and model version history
- Baseline reset flow for replaying the full before/after HIL demo
- KPI monitoring for invalid recall, macro F1, escalation review rate, and pending label ratio
- Retrain outcome label (`Improved`, `Mixed`, `Regressed`, `Baseline`)
- Governance & Audit view with separate escalation-review history and human-feedback history
- Active model/version visibility directly in the UI

### Changed
- Tab wording updated to better reflect the actual workflow
- Retraining now treats contradictory labels as learnable new evidence
- Pending labels are based on unapplied training labels rather than total historical feedback
- Model Monitoring now trends KPIs by model version, not raw retrain order
- Human feedback now records the active model version instead of a hardcoded value

### Fixed
- Legacy and new feedback decision vocabularies are both accepted and canonicalized
- Prevented meaningless retrains when no learnable new records exist
- Added KPI backfill for older manifest entries so historical runs no longer render as 0.0%
- Removed accidental inclusion of escalation-review decisions in training label export

## [v0.10.1.0] - 2026-03-12

### Updates
- Validation error cards, icons, improved layout, demo files recreated
- Demo files updated for confidence-failure scenarios

## [v0.10.0] - 2026-03-11

### Updates
- Extraction summary and prediction results limited to the extraction tab
- Prediction display logic modularized and called once per upload
- Clearer workflow for document review and action

## [v0.9.0] - 2026-03-10

### Major Updates
- Modularized business logic into service modules
- Centralized config, data, and logs folders
- Improved sidebar layout and UI/UX
- Real-time escalation review and human-in-the-loop workflow