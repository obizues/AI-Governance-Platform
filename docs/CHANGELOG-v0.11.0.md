## AI Governance Platform v0.11.0

### Release highlights
- Separated **Escalation Decisions** from **Human Training Labels**
- Added governed retraining with active-model overwrite and model version history
- Added baseline reset to replay the full before/after HIL demo
- Added KPI monitoring focused on invalid recall, macro F1, escalation review rate, and pending label ratio
- Added retrain outcome labeling: `Improved`, `Mixed`, `Regressed`, `Baseline`
- Added governance/audit visibility for escalation review history and human feedback history
- Added active model/version visibility directly in the UI

### What changed operationally
1. Low-confidence document fields are escalated for human review.
2. Operational reviewers make escalation decisions separately from model-training labels.
3. Human training labels with known ground truth are exported for retraining.
4. Retraining creates a new model version, updates the active model, and logs KPIs.
5. Reviewers can compare baseline vs retrained behavior using the reset-to-baseline flow.

### Upgrade notes
- Current application release: **v0.11.0**
- Baseline model version for demo reset: **v0.11.0**
- Retraining now uses only training-eligible human feedback and excludes escalation-review decisions.

### Contributors
- @obizues

---
For issues or enhancement requests, use the GitHub repository issue tracker.
