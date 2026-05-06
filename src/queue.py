from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.filters import ScoredArticle


@dataclass(frozen=True)
class QueueItem:
    slot: int
    scheduled_time_iso: str
    arxiv_id: str
    title: str
    theme: str
    score: int
    practicality: str
    post_html: str = ""
    published: bool = False
    published_at: str | None = None


def build_daily_queue_payload(
    articles: list[ScoredArticle],
    timezone_name: str,
    publish_hour_start: int,
    publish_minute: int,
    target_date: datetime | None = None,
) -> dict:
    tz = ZoneInfo(timezone_name)
    now = datetime.now(tz)
    base_date = (target_date or now).date()

    items: list[dict] = []
    for slot, scored_article in enumerate(articles, start=1):
        scheduled_time = datetime(
            year=base_date.year,
            month=base_date.month,
            day=base_date.day,
            hour=publish_hour_start + slot - 1,
            minute=publish_minute,
            tzinfo=tz,
        )
        item = QueueItem(
            slot=slot,
            scheduled_time_iso=scheduled_time.isoformat(),
            arxiv_id=scored_article.article.arxiv_id,
            title=scored_article.article.title,
            theme=scored_article.theme,
            score=scored_article.score,
            practicality=scored_article.practicality,
            published=False,
            published_at=None,
        )
        items.append(asdict(item))

    return {
        "date": base_date.isoformat(),
        "timezone": timezone_name,
        "status": "ready" if items else "empty",
        "items": items,
    }


def find_due_item(queue_payload: dict, now: datetime | None = None) -> dict | None:
    timezone_name = queue_payload.get("timezone", "Europe/Moscow")
    tz = ZoneInfo(timezone_name)
    current = now or datetime.now(tz)

    for item in queue_payload.get("items", []):
        if item.get("published"):
            continue
        scheduled = datetime.fromisoformat(item["scheduled_time_iso"])
        if scheduled <= current:
            return item
    return None


def mark_item_published(queue_payload: dict, arxiv_id: str, published_at: datetime) -> dict:
    updated_items: list[dict] = []
    for item in queue_payload.get("items", []):
        if item.get("arxiv_id") == arxiv_id and not item.get("published"):
            item = {
                **item,
                "published": True,
                "published_at": published_at.isoformat(),
            }
        updated_items.append(item)

    queue_payload["items"] = updated_items
    queue_payload["status"] = (
        "done" if all(item.get("published") for item in updated_items) else "ready"
    )
    return queue_payload
