from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from src.arxiv_client import fetch_recent_articles
from src.config import Settings, ensure_telegram_settings
from src.filters import select_consumer_friendly_articles
from src.formatter import format_post
from src.queue import build_daily_queue_payload, find_due_item, mark_item_published
from src.storage import (
    load_history,
    load_posted_ids,
    load_queue,
    save_history,
    save_posted_ids,
    save_queue,
)
from src.telegram_client import send_message


def run_pipeline(settings: Settings) -> dict:
    if not settings.dry_run:
        ensure_telegram_settings(settings)

    posted_ids = load_posted_ids(settings.posted_storage_path)
    articles = fetch_recent_articles(
        categories=settings.arxiv_categories,
        max_results=settings.arxiv_max_results,
    )
    selected = select_consumer_friendly_articles(
        articles=articles,
        post_limit=settings.post_limit,
        posted_ids=posted_ids,
    )

    if not selected:
        return {
            "fetched": len(articles),
            "selected": 0,
            "published": 0,
            "skipped_reason": "No consumer-friendly articles matched the current rules.",
        }

    published_count = 0
    history = load_history(settings.history_storage_path)

    for scored_article in selected:
        message = format_post(scored_article)

        if settings.dry_run:
            print("\n" + "=" * 80)
            print(message)
            print("=" * 80 + "\n")
        else:
            send_message(
                bot_token=settings.telegram_bot_token,
                chat_id=settings.telegram_chat_id,
                text=message,
            )
            posted_ids.add(scored_article.article.arxiv_id)
            history.append(
                {
                    "arxiv_id": scored_article.article.arxiv_id,
                    "title": scored_article.article.title,
                    "theme": scored_article.theme,
                    "practicality": scored_article.practicality,
                    "published_at": scored_article.article.published,
                    "score": scored_article.score,
                }
            )

        published_count += 1

    if not settings.dry_run:
        save_posted_ids(settings.posted_storage_path, posted_ids)
        save_history(settings.history_storage_path, history)

    return {
        "fetched": len(articles),
        "selected": len(selected),
        "published": published_count,
        "skipped_reason": "",
    }


def build_daily_queue(settings: Settings) -> dict:
    queue_payload = load_queue(settings.daily_queue_path)
    now = datetime.now(ZoneInfo(settings.publish_timezone))
    today = now.date().isoformat()

    if queue_payload.get("date") == today and queue_payload.get("items"):
        return {
            "fetched": 0,
            "selected": len(queue_payload.get("items", [])),
            "queue_status": queue_payload.get("status", "ready"),
            "skipped_reason": "Queue for today already exists.",
        }

    posted_ids = load_posted_ids(settings.posted_storage_path)
    articles = fetch_recent_articles(
        categories=settings.arxiv_categories,
        max_results=settings.arxiv_max_results,
    )
    selected = select_consumer_friendly_articles(
        articles=articles,
        post_limit=settings.post_limit,
        posted_ids=posted_ids,
    )

    queue_payload = build_daily_queue_payload(
        articles=selected,
        timezone_name=settings.publish_timezone,
        publish_hour_start=settings.publish_hour_start,
        publish_minute=settings.publish_minute,
        target_date=now,
    )
    for item, scored_article in zip(queue_payload.get("items", []), selected, strict=False):
        item["post_html"] = format_post(scored_article)

    if not settings.dry_run:
        save_queue(settings.daily_queue_path, queue_payload)

    return {
        "fetched": len(articles),
        "selected": len(selected),
        "queue_status": queue_payload.get("status", "empty"),
        "skipped_reason": "" if selected else "No suitable articles for daily queue.",
    }


def publish_due_post(settings: Settings) -> dict:
    if not settings.dry_run:
        ensure_telegram_settings(settings)

    queue_payload = load_queue(settings.daily_queue_path)
    if not queue_payload.get("items"):
        return {
            "published": 0,
            "published_title": "",
            "skipped_reason": "Daily queue is empty.",
        }

    now = datetime.now(ZoneInfo(settings.publish_timezone))
    today = now.date().isoformat()
    if queue_payload.get("date") != today:
        if not settings.dry_run:
            save_queue(
                settings.daily_queue_path,
                {
                    "date": today,
                    "timezone": settings.publish_timezone,
                    "status": "empty",
                    "items": [],
                },
            )
        return {
            "published": 0,
            "published_title": "",
            "skipped_reason": "Queue is stale and was reset for the new day.",
        }

    due_item = find_due_item(queue_payload)
    if not due_item:
        return {
            "published": 0,
            "published_title": "",
            "skipped_reason": "No due post right now.",
        }
    message = due_item.get("post_html", "")
    if not message:
        return {
            "published": 0,
            "published_title": "",
            "skipped_reason": "Due post has no prepared content.",
        }

    posted_ids = load_posted_ids(settings.posted_storage_path)
    history = load_history(settings.history_storage_path)

    if settings.dry_run:
        print(message)
    else:
        send_message(
                bot_token=settings.telegram_bot_token,
                chat_id=settings.telegram_chat_id,
                text=message,
            )
        posted_ids.add(due_item["arxiv_id"])
        history.append(
            {
                "arxiv_id": due_item["arxiv_id"],
                "title": due_item["title"],
                "theme": due_item["theme"],
                "practicality": due_item["practicality"],
                "published_at": now.isoformat(),
                "score": due_item["score"],
            }
        )
        queue_payload = mark_item_published(queue_payload, due_item["arxiv_id"], now)
        save_posted_ids(settings.posted_storage_path, posted_ids)
        save_history(settings.history_storage_path, history)
        save_queue(settings.daily_queue_path, queue_payload)

    return {
        "published": 1,
        "published_title": due_item["title"],
        "skipped_reason": "",
    }
