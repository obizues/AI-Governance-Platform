# Changelog

## [v1.1.0] - 2026-03-15

### Added
- Retrain governance gate UX in Model Monitoring:
  - blocks production promotion when candidate KPIs regress
  - shows KPI deltas versus active production model
  - supports explicit Force Promote with reviewer and written justification
- Compatibility retrain invocation wrapper in UI to handle runtime signature drift safely

### Changed
- Application/UI and documentation version references updated to **v1.1.0**
- Sidebar/About/Tech Stack/System Design/Architecture/README language updated to explicitly include guardrail behavior

## [v1.0.0] - 2026-03-15

### Added
- AI-native extraction path via `LLMExtractionService`
- Local-first provider support for Ollama with OpenAI-compatible alternative support
- Sidebar LLM runtime status card showing mode/provider/model/health
- Explicit **Re-run selected ZIP** control for deliberate reprocessing behavior
- Dedicated v1.0.0 release notes: `docs/CHANGELOG-v1.0.0.md`

### Changed
- Application/UI version upgraded to **v1.0.0**
- Sidebar app summary, Tech Stack, and System Design Notes rewritten for AI-native architecture
- Architecture documentation and diagrams updated to include LLM/hybrid extraction flow and provider integration
- Upload rerun behavior now avoids unintended re-extraction during unrelated Streamlit reruns
- Retrain promotion now includes a governance guardrail (block on KPI regression unless force-promoted with reviewer accountability)

## [v0.11.4] - 2026-03-15

### Added
- New `LLMExtractionService` for AI-native document field extraction from PDF text
- Provider-agnostic extraction options via environment configuration:
  - `LLM_PROVIDER=openai` (OpenAI-compatible API)
  - `LLM_PROVIDER=ollama` (local Ollama endpoint)

### Changed
- `extract_and_validate()` now supports extraction modes via `AI_EXTRACTION_MODE`:
  - `rules` (default, deterministic parser)
  - `llm` (LLM-only extraction)
  - `hybrid` (rules + LLM enrichment)
- Added safe fallback to rules when LLM extraction is unavailable or errors
- Added extraction metadata in results (`extraction_method`, `llm_provider`, `llm_model`, `llm_error`)
- Documentation updated with setup instructions for LLM extraction mode

## [v0.11.3] - 2026-03-15

### Fixed
- Step 1 upload flow now re-runs extraction when selecting the same ZIP again (not only when filename changes)
- Upload dedupe gate now keys off a per-upload token (name + size + upload id) instead of filename-only state

### Changed
- Application/UI version bumped to v0.11.3

## [v0.11.2] - 2026-03-15

### Changed
- **Architecture refactor**: moved all business logic out of `app.py` into dedicated service classes
  - New `ModelMonitoringService` — manifest reading, metric extraction from classification reports, semver helpers, active model badge metadata, retrain outcome classification, KPI trend dataframe construction, pending label filter derivation
  - New `ExtractionOrchestrationService` — full ZIP processing pipeline: interaction log reset, loan package UUID generation, per-PDF extraction + inference loop, escalation threshold decision, CSV row writing, escalated PDF saving
  - Extended `EscalationService` — added `extract_escalated_field()`, `normalize_document_type()`, `build_governance_feedback_payload()` helper methods
- Removed eight duplicate domain classes (`LoanApplication`, `Disclosure`, `CreditReport`, etc.) from `app.py`; canonical definitions remain in `extraction_service.py`
- Consolidated `reviewer_names` list into a single module-level `REVIEWER_NAMES` constant
- Unified `FeedbackService` instantiation across tabs (consistent `log_dir="logs"`)
- Moved all inline `import` statements to the top-level import block
- Replaced redundant inline manifest reading in the Model Monitoring tab with `ModelMonitoringService` method calls

### Unchanged
- All behaviour, UI, and API contracts identical to v0.11.1
- 12/12 tests passing

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