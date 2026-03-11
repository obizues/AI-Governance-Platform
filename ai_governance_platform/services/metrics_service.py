"""
Metrics & KPIs Service Module
Centralizes metrics calculation and KPI logic for the AI Governance Platform.
"""

import os
import csv
from typing import List, Dict, Any

class MetricsService:
    def __init__(self, log_dir="logs", log_file="kpis.csv"):
        self.log_dir = log_dir
        self.log_file = log_file
        self.log_path = os.path.join(self.log_dir, self.log_file)
        os.makedirs(self.log_dir, exist_ok=True)

    def log_kpi(self, kpi_name: str, value: Any, details: Dict[str, Any] = None):
        """
        Logs a KPI metric to the CSV log file.
        Args:
            kpi_name (str): Name of the KPI.
            value (Any): Value of the KPI.
            details (dict, optional): Additional details.
        """
        import datetime
        timestamp = datetime.datetime.utcnow().isoformat()
        row = {
            "timestamp": timestamp,
            "kpi_name": kpi_name,
            "value": value
        }
        if details:
            row.update(details)
        write_header = not os.path.exists(self.log_path)
        with open(self.log_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if write_header:
                writer.writeheader()
            writer.writerow(row)

    def get_kpis(self, filter_name: str = None) -> List[Dict[str, Any]]:
        """
        Retrieves KPI logs, optionally filtered by KPI name.
        Args:
            filter_name (str, optional): Filter KPIs by name.
        Returns:
            List[dict]: List of KPI entries.
        """
        if not os.path.exists(self.log_path):
            return []
        with open(self.log_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            kpis = [row for row in reader]
        if filter_name:
            kpis = [kpi for kpi in kpis if kpi["kpi_name"] == filter_name]
        return kpis

    def summarize_kpis(self) -> Dict[str, Any]:
        """
        Summarizes KPIs for reporting or analytics.
        Returns:
            dict: Summary statistics (counts, averages, etc.)
        """
        kpis = self.get_kpis()
        summary = {}
        for kpi in kpis:
            name = kpi.get("kpi_name", "unknown")
            value = float(kpi.get("value", 0))
            if name not in summary:
                summary[name] = {"count": 0, "total": 0}
            summary[name]["count"] += 1
            summary[name]["total"] += value
        for name in summary:
            summary[name]["average"] = summary[name]["total"] / summary[name]["count"] if summary[name]["count"] else 0
        return summary
