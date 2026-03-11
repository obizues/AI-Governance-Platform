---
# AI Governance & Evaluation Platform Architecture

## Version: v0.9.1

### Key Features

- Modularized business logic into service modules (extraction, validation, audit logging, feedback, file management, metrics, policy, provider)
- Centralized config, data, and logs folders
- Real-time escalation review and human-in-the-loop workflow
- Document extraction, validation, and confidence scoring
- Audit log tab with full review history
- Sequential loan numbering and improved UI/UX
- Feedback logging and summary for continuous improvement
- System Health KPIs for operational visibility
- Streamlit-based modern UI for business users
- Open-source, extensible Python codebase
- Demo Files sidebar expander with download buttons
- Dynamic listing of sample_zips files
- Streamlit download buttons for demo files
- Designed for CTOs, CEOs, hiring managers, and PE operators
...existing code...


## Component Diagram

```mermaid
graph TD
  User -->|Interacts| Streamlit_UI
  Streamlit_UI -->|Calls| Extraction_Service
  Streamlit_UI -->|Calls| Validation_Service
  Streamlit_UI -->|Calls| Audit_Logging_Service
  Streamlit_UI -->|Calls| Feedback_Service
  Streamlit_UI -->|Calls| Metrics_Service
  Streamlit_UI -->|Calls| Policy_Service
  Streamlit_UI -->|Calls| Provider_Service
  Extraction_Service --> Data
  Validation_Service --> Data
  Audit_Logging_Service --> Logs
  Feedback_Service --> Logs
  Metrics_Service --> Logs
  Policy_Service --> Config
  Provider_Service --> Data
  Streamlit_UI -->|Displays| UI_Tabs
  UI_Tabs --> Audit_Log
  UI_Tabs --> Escalation_Review
  UI_Tabs --> Document_Extraction
  UI_Tabs --> Confidence_Scoring
  UI_Tabs --> Feedback
  UI_Tabs --> KPIs
  Config -->|Policy| Policy_Service
  Data -->|Documents| Extraction_Service
  Logs -->|Audit| Audit_Logging_Service
  Logs -->|Feedback| Feedback_Service
  Logs -->|Metrics| Metrics_Service
```

## Data Flow
- User submits query via UI
- Policy engine evaluates risk and applies controls
- Audit logger records interaction
- Feedback logger captures user feedback
- Metrics module computes KPIs
- All logs are stored in CSV/JSON for compliance and reporting

## Extensibility
- Add new policy rules in `config/policy.yaml`
- Extend feedback logic in `services/feedback_service.py`
- Add new metrics in `services/metrics_service.py`
- UI enhancements via Streamlit components

## Deployment
- Streamlit Cloud, local, or containerized environments
- All processing is local; no data leaves the user's environment