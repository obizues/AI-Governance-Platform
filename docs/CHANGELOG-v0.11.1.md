## AI Governance Platform v0.11.1

> Historical release note. For current release details, see `CHANGELOG-v1.2.0.md`.

### Release highlights
- Full sidebar and About-panel copy aligned to the final v0.11.1 HIL + retraining workflow
- Active model badge logic corrected so baseline resets and legacy manifest entries display accurate labels
- Governance & Audit tab escalation history now reads the persistent structured review log instead of the session-only interaction log
- Tech Stack and System Design Notes sidebar expanders reflect the actual implementation and architecture

### What changed operationally
1. The **About This Project** sidebar section describes the full end-to-end governance cycle accurately.
2. The **Tech Stack** expander lists every real stack component: scikit-learn, joblib, pdfplumber, matplotlib, Altair, Plotly, YAML config, and Pytest.
3. The **System Design Notes** expander explains the actual architectural decisions: service separation, governance/training label isolation, manifest-driven retraining, versioned deployment, and baseline reset.
4. The **Active Model** sidebar badge now correctly distinguishes baseline resets from feedback retrains, and no longer surfaces a stale v0.10.0 label after a version upgrade.
5. The **Governance & Audit** tab escalation history reads from `logs/feedback_log.csv` (persistent across sessions) so reviewed escalations are never lost when a new ZIP is uploaded.

### Upgrade notes
- Current application release: **v0.11.1**
- Baseline model version for demo reset: **v0.11.1**
- No schema or data-contract changes. Existing `feedback_log.csv` and `retrain_manifest.json` are fully compatible.

### Contributors
- @obizues

---
For issues or enhancement requests, use the GitHub repository issue tracker.
