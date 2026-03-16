## AI Document Governance Platform v1.1.0

### Release theme
Governed promotion guardrails for safer model lifecycle control.

### Major highlights
- Retrain candidate promotion is now governance-gated in the UI:
  - candidate is blocked from production deployment when key KPIs regress
  - operator sees explicit KPI deltas (accuracy, invalid recall, macro F1) versus current production model
  - force promotion requires reviewer identity, explicit acknowledgment, and written justification
- Retrain manifest records force-promote and regression context for auditability
- UI retrain calls now include compatibility handling for runtime signature mismatches

### Documentation updates
- Sidebar feature bullets now call out regression guardrails directly
- README, architecture, docs index, and release history updated to reflect guardrail-first governance posture

### Version notes
- Application release: **v1.1.0**
- Baseline reset model for demo replay: **v0.11.1**

### Contributors
- @obizues
