"""Persistent record storage backed by a JSON file.

This is the source of truth. The Excel tracker is generated from it on
demand, so the spreadsheet is always consistent with the saved records.
Swap this module for a database later without touching the routers.
"""
import json
import os
import threading
from datetime import datetime, timezone
from typing import List, Dict, Optional

from . import config

_lock = threading.Lock()


def _ensure_file() -> None:
    os.makedirs(config.DATA_DIR, exist_ok=True)
    if not os.path.exists(config.RECORDS_FILE):
        with open(config.RECORDS_FILE, "w") as f:
            json.dump([], f)


def _read() -> List[Dict]:
    _ensure_file()
    with open(config.RECORDS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _write(records: List[Dict]) -> None:
    _ensure_file()
    with open(config.RECORDS_FILE, "w") as f:
        json.dump(records, f, indent=2)


def list_records() -> List[Dict]:
    return _read()


def get_record(record_id: str) -> Optional[Dict]:
    return next((r for r in _read() if r.get("id") == record_id), None)


def add_record(data: Dict) -> Dict:
    with _lock:
        records = _read()
        now = datetime.now(timezone.utc).isoformat()
        data["id"] = str(int(datetime.now().timestamp() * 1000))
        data["created_at"] = now
        data["updated_at"] = now
        records.append(data)
        _write(records)
        return data


def update_record(record_id: str, updates: Dict) -> Optional[Dict]:
    with _lock:
        records = _read()
        for i, r in enumerate(records):
            if r.get("id") == record_id:
                records[i] = {
                    **r,
                    **updates,
                    "id": record_id,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
                _write(records)
                return records[i]
        return None


def delete_record(record_id: str) -> bool:
    with _lock:
        records = _read()
        new_records = [r for r in records if r.get("id") != record_id]
        if len(new_records) == len(records):
            return False
        _write(new_records)
        return True


def stats() -> Dict[str, int]:
    records = _read()
    return {
        "total": len(records),
        "open": sum(1 for r in records if (r.get("Status") or "").upper() == "OPEN"),
        "pending": sum(1 for r in records if r.get("Case_Status") == "Pending Driver Info"),
        "dismissed": sum(1 for r in records if r.get("Case_Status") == "Dismissed"),
    }
