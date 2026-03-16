"""
File Management Service Module
Handles CSV, JSON, and log file operations for the AI Document Governance Platform.
"""

import os
import csv
import json
from typing import List, Dict, Any

class FileManagementService:
    def __init__(self, base_dir="logs"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def read_csv(self, filename: str) -> List[Dict[str, Any]]:
        path = os.path.join(self.base_dir, filename)
        if not os.path.exists(path):
            return []
        with open(path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [row for row in reader]

    def write_csv(self, filename: str, rows: List[Dict[str, Any]]):
        path = os.path.join(self.base_dir, filename)
        if not rows:
            return
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    def append_csv(self, filename: str, row: Dict[str, Any], fieldnames: List[str] = None):
        path = os.path.join(self.base_dir, filename)
        write_header = not os.path.exists(path)
        headers = fieldnames or list(row.keys())
        with open(path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            if write_header:
                writer.writeheader()
            writer.writerow(row)

    def read_json(self, filename: str) -> Any:
        path = os.path.join(self.base_dir, filename)
        if not os.path.exists(path):
            return None
        with open(path, mode="r", encoding="utf-8") as f:
            return json.load(f)

    def write_json(self, filename: str, data: Any):
        path = os.path.join(self.base_dir, filename)
        with open(path, mode="w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def backup_file(self, filename: str, backup_dir="backup"):
        src = os.path.join(self.base_dir, filename)
        dst_dir = os.path.join(self.base_dir, backup_dir)
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, filename)
        if os.path.exists(src):
            with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
                fdst.write(fsrc.read())

    def delete_file(self, filename: str):
        path = os.path.join(self.base_dir, filename)
        if os.path.exists(path):
            os.remove(path)
