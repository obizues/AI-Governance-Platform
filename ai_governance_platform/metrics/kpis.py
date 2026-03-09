def refresh_system_health_kpi():
    """
    Refreshes and returns system health KPIs such as uptime, memory usage, CPU load, and status.
    Returns a dict with health metrics.
    """
    import psutil
    import time
    health_kpi = {}
    health_kpi["uptime_seconds"] = time.time() - psutil.boot_time()
    health_kpi["memory_percent"] = psutil.virtual_memory().percent
    health_kpi["cpu_percent"] = psutil.cpu_percent(interval=1)
    health_kpi["status"] = "healthy" if health_kpi["cpu_percent"] < 80 and health_kpi["memory_percent"] < 80 else "warning"
    return health_kpi

import pandas as pd
import os

def compute_kpis(log_path, feedback_path):
    kpis = {
        "total_queries": 0,
        "deny_rate": 0.0,
        "escalation_rate": 0.0,
        "avg_latency": 0.0,
        "positive_feedback_rate": 0.0,
        "trust_score": 0.0,
        "eval_pass_rate": None,
        "eval_avg_score": None
    }
    if os.path.exists(log_path):
        df = pd.read_csv(log_path)
        kpis["total_queries"] = len(df)
        kpis["deny_rate"] = (df["decision"] == "deny").mean() if len(df) else 0.0
        kpis["escalation_rate"] = (df["decision"] == "escalate").mean() if len(df) else 0.0
        if "response_time_ms" in df:
            if not pd.api.types.is_numeric_dtype(df["response_time_ms"]):
                df["response_time_ms"] = pd.to_numeric(df["response_time_ms"], errors="coerce")
            kpis["avg_latency"] = df["response_time_ms"].mean()
        else:
            kpis["avg_latency"] = 0.0
    if os.path.exists(feedback_path):
        try:
            fdf = pd.read_csv(feedback_path)
            if fdf.empty:
                raise pd.errors.EmptyDataError()
        except pd.errors.EmptyDataError:
            # Return default KPIs if feedback log is empty
            return {
                "total_queries": 0,
                "deny_rate": 0.0,
                "escalation_rate": 0.0,
                "avg_latency": 0.0,
                "positive_feedback_rate": 0.0,
                "trust_score": 0.0
            }
        kpis["positive_feedback_rate"] = (fdf["feedback"] == "👍").mean() if len(fdf) else 0.0
    # Simple trust score: positive feedback rate minus deny+escalate rate
    kpis["trust_score"] = kpis["positive_feedback_rate"] - (kpis["deny_rate"] + kpis["escalation_rate"])

    # Add evaluation metrics if available
    eval_report_path = os.path.abspath(os.path.join(os.path.dirname(feedback_path), "..", "ai_governance_platform", "evaluation", "evaluation_report.json"))
    if os.path.exists(eval_report_path):
        import json
        with open(eval_report_path, "r", encoding="utf-8") as f:
            try:
                report = json.load(f)
                summary = report.get("summary", {})
                kpis["eval_pass_rate"] = summary.get("pass_rate")
                kpis["eval_avg_score"] = summary.get("average_score")
            except Exception:
                pass
    return kpis
