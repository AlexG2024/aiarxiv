from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    telegram_chat_id: str
    arxiv_categories: list[str]
    post_limit: int
    arxiv_max_results: int
    dry_run: bool
    posted_storage_path: Path
    history_storage_path: Path
    daily_queue_path: Path
    publish_timezone: str
    publish_hour_start: int
    publish_hour_end: int
    publish_minute: int


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_categories(raw_value: str | None) -> list[str]:
    if not raw_value:
        return ["cs.AI", "cs.LG", "cs.CL", "cs.CV"]
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def _load_local_env(env_path: Path = Path(".env")) -> None:
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()

        if key and key not in os.environ:
            os.environ[key] = value


def load_settings() -> Settings:
    _load_local_env()
    dry_run = _parse_bool(os.getenv("DRY_RUN"), default=False)
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    storage_path = Path(os.getenv("POSTED_STORAGE_PATH", "data/posted.json"))
    history_path = Path(os.getenv("HISTORY_STORAGE_PATH", "data/history.json"))
    daily_queue_path = Path(os.getenv("DAILY_QUEUE_PATH", "data/daily_queue.json"))

    return Settings(
        telegram_bot_token=bot_token,
        telegram_chat_id=chat_id,
        arxiv_categories=_parse_categories(os.getenv("ARXIV_CATEGORIES")),
        post_limit=max(1, int(os.getenv("POST_LIMIT", "10"))),
        arxiv_max_results=max(10, int(os.getenv("ARXIV_MAX_RESULTS", "300"))),
        dry_run=dry_run,
        posted_storage_path=storage_path,
        history_storage_path=history_path,
        daily_queue_path=daily_queue_path,
        publish_timezone=os.getenv("PUBLISH_TIMEZONE", "Europe/Moscow"),
        publish_hour_start=int(os.getenv("PUBLISH_HOUR_START", "8")),
        publish_hour_end=int(os.getenv("PUBLISH_HOUR_END", "17")),
        publish_minute=int(os.getenv("PUBLISH_MINUTE", "10")),
    )


def ensure_telegram_settings(settings: Settings) -> None:
    if not settings.telegram_bot_token:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN")
    if not settings.telegram_chat_id:
        raise ValueError("Missing TELEGRAM_CHAT_ID")
