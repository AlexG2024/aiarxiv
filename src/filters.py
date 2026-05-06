from __future__ import annotations

from dataclasses import dataclass

from src.arxiv_client import Article


@dataclass(frozen=True)
class ScoredArticle:
    article: Article
    score: int
    theme: str
    practicality: str
    whitelist_hits: tuple[str, ...]
    blacklist_hits: tuple[str, ...]


POSITIVE_KEYWORDS = {
    "assistant": 4,
    "agent": 4,
    "chatbot": 4,
    "conversational": 4,
    "everyday": 4,
    "daily": 3,
    "search": 4,
    "retrieval": 4,
    "productivity": 4,
    "education": 4,
    "health": 4,
    "medical": 4,
    "symptom": 4,
    "doctor": 3,
    "patient": 3,
    "image": 3,
    "video": 3,
    "audio": 3,
    "voice": 3,
    "multimodal": 3,
    "language model": 3,
    "large language model": 3,
    "llm": 3,
    "reasoning": 2,
    "consumer": 3,
    "user": 2,
    "safety": 2,
    "recommendation": 3,
    "personalized": 3,
    "workflow": 2,
}

NEGATIVE_KEYWORDS = {
    "theorem": -5,
    "proof": -5,
    "convergence": -4,
    "asymptotic": -4,
    "posterior": -4,
    "manifold": -3,
    "spectral": -3,
    "admm": -3,
    "mcmc": -4,
    "tensor completion": -4,
    "lagrangian": -3,
    "sample complexity": -4,
    "bound": -3,
    "bounds": -3,
    "differential privacy": -2,
    "bayesian uncertainty quantification": -3,
    "manufacturing": -5,
    "machining": -5,
    "aerospace": -4,
    "inspection": -3,
    "point-cloud": -3,
    "materials science": -7,
    "chemistry": -6,
    "lithology": -7,
    "geology": -6,
    "geological": -6,
    "mineral": -5,
    "petrophysics": -6,
    "catalyst": -5,
    "molecule": -4,
    "molecular": -4,
    "protein folding": -4,
    "hackathon": -5,
    "patent": -7,
    "patent examination": -8,
    "office action": -8,
}

STRONG_PATTERNS = {
    "assistant": 5,
    "agent": 5,
    "workflow": 4,
    "search": 5,
    "retrieval": 5,
    "health": 5,
    "medical": 5,
    "symptom": 5,
    "education": 4,
    "multimodal": 4,
    "audio-visual": 4,
    "interactive": 4,
    "real-world": 5,
    "real world": 5,
    "application": 4,
    "user study": 4,
    "assistant system": 4,
}

WEAK_PATTERNS = {
    "theorem": -6,
    "proof": -6,
    "asymptotic": -5,
    "sample complexity": -5,
    "posterior": -4,
    "spectral": -4,
    "lagrangian": -4,
    "manifold": -4,
    "tensor completion": -5,
    "eigenvalue": -4,
    "variational bound": -4,
    "materials science": -8,
    "chemistry": -7,
    "lithology": -8,
    "geology": -7,
    "geological": -7,
    "petrophysics": -8,
    "mineral": -6,
    "molecular": -5,
    "catalyst": -6,
    "hackathon": -6,
    "patent": -8,
    "patent examination": -9,
    "office action": -9,
}

HARD_EXCLUDE_PATTERNS = (
    "appendix",
    "erratum",
    "withdrawn",
)

CONSUMER_CORE_PATTERNS = (
    "assistant",
    "agent",
    "search",
    "retrieval",
    "health",
    "medical",
    "symptom",
    "education",
    "productivity",
    "chatbot",
    "voice",
    "video",
    "image",
    "audio",
    "multimodal",
    "language model",
    "llm",
    "user",
    "interactive",
)

DOMAIN_SPECIFIC_PATTERNS = (
    "materials science",
    "chemistry",
    "lithology",
    "geology",
    "geological",
    "mineral",
    "petrophysics",
    "catalyst",
    "molecule",
    "molecular",
    "manufacturing",
    "machining",
    "aerospace",
    "patent",
    "patent examination",
    "office action",
)

PRACTICAL_HIGH_PATTERNS = (
    "system",
    "assistant",
    "agent",
    "workflow",
    "clinical",
    "health",
    "search",
    "application",
    "user study",
    "real-world",
)

PRACTICAL_LOW_PATTERNS = (
    "theorem",
    "proof",
    "convergence",
    "asymptotic",
    "sample complexity",
    "posterior",
    "spectral",
    "lagrangian",
)

THEME_RULES = [
    ("red team", "AI safety и надежность"),
    ("red teaming", "AI safety и надежность"),
    ("adversarial", "AI safety и надежность"),
    ("jailbreak", "AI safety и надежность"),
    ("security", "AI safety и надежность"),
    ("safety", "AI safety и надежность"),
    ("medical", "AI в медицине"),
    ("health", "AI в медицине"),
    ("clinical", "AI в медицине"),
    ("symptom", "AI в медицине"),
    ("education", "AI в обучении"),
    ("audio-visual", "multimodal AI"),
    ("multimodal", "multimodal AI"),
    ("image", "AI для изображений"),
    ("video", "AI для видео"),
    ("audio", "AI для аудио"),
    ("voice", "голосовые AI-сценарии"),
    ("search", "поиск и работа с информацией"),
    ("retrieval", "поиск и работа с информацией"),
    ("productivity", "AI для работы и productivity"),
    ("assistant", "AI-ассистенты"),
    ("agent", "AI-агенты"),
    ("recommendation", "рекомендательные AI-системы"),
    ("language model", "языковые модели"),
    ("large language model", "языковые модели"),
    ("llm", "языковые модели"),
]


def _haystack(article: Article) -> str:
    return f"{article.title} {article.summary}".lower()


def _detect_theme(article: Article) -> str:
    title_text = article.title.lower()
    summary_text = article.summary.lower()

    for keyword, theme in THEME_RULES:
        if keyword in title_text:
            return theme

    text = f"{title_text} {summary_text}"
    for keyword, theme in THEME_RULES:
        if keyword in text:
            return theme
    return "прикладной AI"


def _contains_hard_exclude(text: str) -> bool:
    return any(pattern in text for pattern in HARD_EXCLUDE_PATTERNS)


def _collect_hits(text: str, patterns: dict[str, int]) -> tuple[list[str], int]:
    hits: list[str] = []
    total = 0
    for pattern, weight in patterns.items():
        if pattern in text:
            hits.append(pattern)
            total += weight
    return hits, total


def _has_consumer_signal(text: str) -> bool:
    return any(pattern in text for pattern in CONSUMER_CORE_PATTERNS)


def _is_too_domain_specific(text: str) -> bool:
    domain_hits = sum(1 for pattern in DOMAIN_SPECIFIC_PATTERNS if pattern in text)
    return domain_hits >= 2 and not _has_consumer_signal(text)


def _detect_practicality(text: str, score: int) -> str:
    high_hits = sum(1 for pattern in PRACTICAL_HIGH_PATTERNS if pattern in text)
    low_hits = sum(1 for pattern in PRACTICAL_LOW_PATTERNS if pattern in text)

    if score >= 16 or (high_hits >= 3 and low_hits == 0):
        return "high"
    if score <= 5 or low_hits >= 2:
        return "research"
    return "medium"


def score_article(article: Article) -> ScoredArticle | None:
    text = _haystack(article)
    if _contains_hard_exclude(text):
        return None
    if _is_too_domain_specific(text):
        return None

    score = 0

    for keyword, weight in POSITIVE_KEYWORDS.items():
        if keyword in text:
            score += weight

    for keyword, weight in NEGATIVE_KEYWORDS.items():
        if keyword in text:
            score += weight

    whitelist_hits, whitelist_score = _collect_hits(text, STRONG_PATTERNS)
    blacklist_hits, blacklist_score = _collect_hits(text, WEAK_PATTERNS)
    score += whitelist_score + blacklist_score

    if any(category in {"cs.AI", "cs.CL", "cs.CV"} for category in article.categories):
        score += 2

    if len(article.title.split()) <= 18:
        score += 1

    title_words = article.title.lower()
    if any(pattern in title_words for pattern in STRONG_PATTERNS):
        score += 2
    if any(pattern in title_words for pattern in DOMAIN_SPECIFIC_PATTERNS):
        score -= 4

    practicality = _detect_practicality(text, score)

    return ScoredArticle(
        article=article,
        score=score,
        theme=_detect_theme(article),
        practicality=practicality,
        whitelist_hits=tuple(whitelist_hits),
        blacklist_hits=tuple(blacklist_hits),
    )


def select_consumer_friendly_articles(
    articles: list[Article],
    post_limit: int,
    posted_ids: set[str],
) -> list[ScoredArticle]:
    scored: list[ScoredArticle] = []

    for article in articles:
        if article.arxiv_id in posted_ids:
            continue

        candidate = score_article(article)
        if candidate is None:
            continue

        min_score = 14 if candidate.practicality == "high" else 18
        if (
            candidate.score >= min_score
            and len(candidate.whitelist_hits) >= 1
            and candidate.practicality != "research"
        ):
            scored.append(candidate)

    practicality_rank = {"high": 2, "medium": 1, "research": 0}
    scored.sort(
        key=lambda item: (
            practicality_rank[item.practicality],
            item.score,
            len(item.whitelist_hits),
            -len(item.blacklist_hits),
        ),
        reverse=True,
    )
    return scored[:post_limit]
