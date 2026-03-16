## AI Document Governance Platform v1.2.0

Release date: 2026-03-15

### Highlights

- Added first-class Claude support via native Anthropic Messages API
- Added Streamlit Cloud secrets template for Claude deployments
- Improved runtime defaults so configured API keys automatically enable the correct provider/mode
- Added Anthropic endpoint normalization and model fallback behavior for better reliability
- Added a new demo loan package (`home_loan_docs_7.zip`) with exactly two errors, including a negative-value case

### Added

- `LLM_PROVIDER=anthropic` support in `LLMExtractionService`
- `ANTHROPIC_API_KEY` and `ANTHROPIC_BASE_URL` provider settings
- Anthropic-specific runtime health reporting in sidebar status
- Sidebar warning when Anthropic mode is enabled but `ANTHROPIC_API_KEY` is missing
- `.streamlit/secrets.toml.example` template for Streamlit Cloud
- `scripts/generate_home_loan_zip_7.py`
- `sample_zips/home_loan_docs_7.zip`

### Changed

- Provider/mode default selection now prioritizes available credentials:
  - Anthropic key present -> `LLM_PROVIDER=anthropic`, `AI_EXTRACTION_MODE=hybrid`
  - OpenAI key present -> `LLM_PROVIDER=openai`, `AI_EXTRACTION_MODE=hybrid`
  - no key -> local Ollama defaults
- Anthropic endpoint handling now supports both `https://api.anthropic.com` and `https://api.anthropic.com/v1`
- Anthropic model fallback sequence added to handle account-specific model availability
- README, docs index, architecture, app version, and requirements version marker updated to v1.2.0

### Verification notes

- `sample_zips/home_loan_docs_7.zip` verified to produce exactly two errors in pipeline validation:
  - `Disclosure.pdf`: `Fees missing`
  - `Bank_Statement.pdf`: `balance below confidence threshold (...)` with negative value `-1500`

### Versioning

- Application release: **v1.2.0**
- Baseline model version for demo reset remains: **v0.11.1**
