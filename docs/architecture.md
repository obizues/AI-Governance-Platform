---
# System Architecture 🗂️

**Version:** v0.4.0

## Overview
The AI Governance & Evaluation Platform is designed for modularity, auditability, and extensibility. It consists of:
...existing code...

## Component Diagram

```
User
   |
   v
Streamlit UI (app.py)
   |
   v
Audit Logger <----> Policy Engine <----> Feedback Logger
   |
   v
Metrics/KPIs
   |
   v
Logs (CSV, JSON)
```

## Data Flow
- User submits query via UI
- Policy engine evaluates risk and applies controls
- Audit logger records interaction
- Feedback logger captures user feedback
- Metrics module computes KPIs
- All logs are stored in CSV/JSON for compliance and reporting

## Extensibility
- Add new policy rules in `policy/policy.yaml`
- Extend feedback logic in `feedback/`
- Add new metrics in `metrics/`
- UI enhancements via Streamlit components

## Deployment
- Streamlit Cloud, local, or containerized environments
- All processing is local; no data leaves the user's environment