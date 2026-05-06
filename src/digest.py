from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone

from src.formatter import build_russian_title_from_text


THEME_WEEKLY_DESCRIPTIONS = {
    "поиск и работа с информацией": "работа про поиск, retrieval и то, как AI лучше находит и использует нужную информацию.",
    "AI safety и надежность": "работа про безопасность AI и то, как находить слабые места до реального внедрения.",
    "AI в медицине": "работа про прикладные AI-сценарии в медицине и здоровье.",
    "AI-агенты": "работа про агентные системы и автоматизацию сложных действий.",
    "multimodal AI": "работа про модели, которые объединяют несколько типов данных.",
    "языковые модели": "работа про развитие LLM и их практическое применение.",
}


def _parse_iso_datetime(raw_value: str) -> datetime | None:
    if not raw_value:
        return None

    try:
        return datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _sentence_case(text: str) -> str:
    if not text:
        return text
    return text[0].upper() + text[1:]


def build_weekly_digest(records: list[dict], now: datetime | None = None) -> str:
    if now is None:
        now = datetime.now(timezone.utc)

    since = now - timedelta(days=7)
    recent_records = [
        record
        for record in records
        if (dt := _parse_iso_datetime(record.get("published_at", ""))) and dt >= since
    ]

    if not recent_records:
        return "За последние 7 дней в истории публикаций пока нет данных для weekly digest."

    theme_counter = Counter(record.get("theme", "Без темы") for record in recent_records)
    top_articles = sorted(
        recent_records,
        key=lambda item: (item.get("score", 0), item.get("practicality") == "high"),
        reverse=True,
    )[:3]

    lines = [
        "<b>Главное за неделю в AI arXiv</b>",
        "",
        f"За неделю в канале вышло <b>{len(recent_records)}</b> публикации.",
        "",
        "<b>Что почитать из лучшего:</b>",
    ]

    for index, record in enumerate(top_articles, start=1):
        theme = record.get("theme", "Без темы")
        title = record.get("title", "Без названия")
        description = THEME_WEEKLY_DESCRIPTIONS.get(
            theme,
            "работа про прикладной AI и его использование в реальных сценариях.",
        )
        description = _sentence_case(description)
        arxiv_id = record.get("arxiv_id", "")
        link = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else ""
        russian_title = build_russian_title_from_text(theme=theme, title_text=title)

        item_lines = [
            f"{index}. <b>{russian_title}</b>",
            f"<i>{title}</i>",
            description,
        ]
        if link:
            item_lines.append(f"<a href=\"{link}\">Читать на arXiv</a>")

        lines.append("\n".join(item_lines))
        if index != len(top_articles):
            lines.append("")

    return "\n".join(lines)
