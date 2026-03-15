## AI Governance Platform v1.0.0

### Release theme
AI-native extraction + governed human oversight + auditable continuous improvement.

### Major highlights
- AI-native document extraction integrated through `LLMExtractionService`
- Local-first LLM runtime support using Ollama (`LLM_PROVIDER=ollama`) with optional OpenAI-compatible provider support
- Runtime extraction mode control (`rules`, `llm`, `hybrid`) with safe deterministic fallback on provider failures
- Sidebar LLM status card showing mode, provider, model, and runtime health
- Upload flow improved with explicit **Re-run selected ZIP** control to avoid expensive unintended reruns during unrelated tab actions

### Governance and safety posture
- Operational escalation decisions remain separated from training labels
- Only training-eligible human labels flow into retraining
- Model retraining remains manifest-driven with version history and KPI tracking
- Baseline reset retained for replayable before/after governance demos

### Version notes
- Application release: **v1.0.0**
- Baseline reset model for demo replay: **v0.11.1**
- Backward-compatible with existing logs and manifest schema

### Contributors
- @obizues
