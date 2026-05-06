from __future__ import annotations

import json
from pathlib import Path


def load_posted_ids(storage_path: Path) -> set[str]:
    if not storage_path.exists():
        return set()

    raw = json.loads(storage_path.read_text(encoding="utf-8"))
    return {item for item in raw if isinstance(item, str)}


def save_posted_ids(storage_path: Path, posted_ids: set[str]) -> None:
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    payload = sorted(posted_ids)
    storage_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_history(storage_path: Path) -> list[dict]:
    if not storage_path.exists():
        return []

    raw = json.loads(storage_path.read_text(encoding="utf-8"))
    return [item for item in raw if isinstance(item, dict)]


def save_history(storage_path: Path, records: list[dict]) -> None:
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    storage_path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_queue(storage_path: Path) -> dict:
    if not storage_path.exists():
        return {"date": "", "timezone": "Europe/Moscow", "status": "empty", "items": []}

    raw = json.loads(storage_path.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {"date": "", "timezone": "Europe/Moscow", "status": "empty", "items": []}


def save_queue(storage_path: Path, payload: dict) -> None:
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    storage_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
