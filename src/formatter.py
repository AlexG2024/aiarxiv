from __future__ import annotations

from datetime import datetime
import html

from src.filters import ScoredArticle


GENERAL_DESCRIPTION_TEMPLATES = (
    "Авторы представили {artifact}, который помогает AI {action_hint}.",
    "В центре статьи {artifact}, который помогает AI {action_hint}.",
    "Работа описывает {artifact}, который помогает AI {action_hint}.",
)

WHAT_DONE_TEMPLATES = (
    "Авторы {contribution_hint} и показывают, как AI может {action_hint}.",
    "В статье {contribution_hint} и разбирают, как AI может {action_hint}.",
    "Исследователи {contribution_hint} и объясняют, как AI может {action_hint}.",
)

RECOMMENDATION_PREFIXES = (
    "Стоит обратить внимание на то, как",
    "Полезно смотреть, как",
    "Имеет смысл следить за тем, как",
)

THEME_PROBLEMS = {
    "AI-ассистенты": "уменьшают число ручных действий, делают помощь AI более последовательной и упрощают выполнение повседневных задач",
    "AI-агенты": "снижают долю ручной координации, помогают автоматизировать цепочки действий и делают AI полезнее в сложных workflow",
    "AI safety и надежность": "помогают раньше находить уязвимости, снижать риски и делать поведение AI более предсказуемым",
    "поиск и работа с информацией": "снижают шум в поиске, помогают быстрее находить нужный контекст и улучшают качество итогового ответа",
    "AI в медицине": "помогают быстрее ориентироваться в симптомах, снижать неопределенность на первом этапе и делать health-сервисы понятнее для пользователя",
    "AI в обучении": "помогают объяснять материал понятнее, подстраивать обучение под человека и снижать барьер входа в сложные темы",
    "AI для изображений": "упрощают создание, анализ и редактирование визуального контента в понятных сценариях",
    "AI для видео": "снижают объем ручной работы с видео и делают визуальные AI-инструменты полезнее в реальной задаче",
    "AI для аудио": "помогают лучше разбирать речь, работать с аудиоданными и снижать ошибки в голосовых сценариях",
    "голосовые AI-сценарии": "делают голосовое взаимодействие с AI понятнее, удобнее и устойчивее в реальном использовании",
    "multimodal AI": "помогают объединять разные типы данных в одном сценарии и делают AI ближе к реальному способу восприятия информации человеком",
    "языковые модели": "снижают трение в работе с текстом, помогают быстрее получать ответы и делают AI полезнее в повседневных задачах",
    "AI для работы и productivity": "снимают рутину, экономят время и помогают быстрее проходить повторяющиеся рабочие процессы",
    "рекомендательные AI-системы": "помогают лучше подбирать контент, товары или решения и снижают перегрузку выбором",
    "прикладной AI": "помогают переносить AI из исследований в реальные пользовательские сценарии",
}

THEME_USE_CASES = {
    "AI-ассистенты": "в корпоративных помощниках, чат-ботах и рабочих AI-сценариях",
    "AI-агенты": "в автоматизации задач, многошаговых workflow и AI-операторах",
    "AI safety и надежность": "в проверке AI-продуктов перед запуском и в настройке безопасного поведения моделей",
    "поиск и работа с информацией": "в поиске по документам, внутренних базах знаний и исследовательских задачах",
    "AI в медицине": "в health-приложениях, цифровом триаже и медицинских помощниках",
    "AI в обучении": "в обучающих сервисах, AI-репетиторах и системах объяснения материала",
    "AI для изображений": "в генерации, анализе и редактировании изображений",
    "AI для видео": "в видеоредакторах, анализе видео и автоматизации визуального контента",
    "AI для аудио": "в транскрибации, голосовых сервисах и обработке звука",
    "голосовые AI-сценарии": "в голосовых помощниках, call-центрах и voice UI",
    "multimodal AI": "в сервисах, где AI одновременно работает с текстом, изображениями и аудио",
    "языковые модели": "в чат-ботах, поиске, письме, анализе текста и AI-помощниках",
    "AI для работы и productivity": "в автоматизации рутины, документов и внутренних рабочих процессов",
    "рекомендательные AI-системы": "в лентах, маркетплейсах и персонализированных рекомендациях",
    "прикладной AI": "в прикладных AI-сценариях для работы, обучения и повседневных задач",
}

THEME_RECOMMENDATIONS = {
    "AI-ассистенты": "стоит следить за тем, как такие помощники подключают инструменты, работают с памятью и справляются с реальными задачами",
    "AI-агенты": "имеет смысл смотреть не только на идею агента, но и на качество orchestration, tool use и контроля ошибок",
    "AI safety и надежность": "полезно смотреть, как команды проверяют модели на уязвимости еще до выхода в продукт",
    "поиск и работа с информацией": "стоит обратить внимание на то, как система ищет контекст, ранжирует результаты и проверяет качество ответа",
    "AI в медицине": "важно воспринимать такие работы как исследование направления, а не как готовую замену врачу или медицинскому совету",
    "AI в обучении": "имеет смысл смотреть, улучшает ли AI не только ответы, но и само понимание материала",
    "AI для изображений": "полезно следить за тем, где модель реально помогает пользователю, а не просто делает красивую демо-генерацию",
    "AI для видео": "стоит смотреть на практическую пользу: скорость, качество и управляемость результата",
    "AI для аудио": "обращайте внимание на качество распознавания, задержку и устойчивость на реальных данных",
    "голосовые AI-сценарии": "важно смотреть, насколько естественно и надежно система ведет диалог голосом",
    "multimodal AI": "стоит следить, насколько хорошо модель связывает несколько типов данных, а не просто обрабатывает их по отдельности",
    "языковые модели": "полезно смотреть, становится ли модель реально полезнее в задачах пользователя, а не только сильнее в benchmark",
    "AI для работы и productivity": "стоит оценивать, дает ли решение реальную экономию времени в повседневной работе",
    "рекомендательные AI-системы": "имеет смысл смотреть на качество персонализации и то, не становится ли система слишком навязчивой",
    "прикладной AI": "полезно смотреть, можно ли перенести идею из статьи в понятный пользовательский сценарий",
}

THEME_CONCLUSIONS = {
    "AI-ассистенты": "AI-ассистенты становятся полезнее, когда их проверяют не на демо, а на реальных задачах пользователя.",
    "AI-агенты": "Главный вопрос для агентных систем уже не только в автономности, но и в надежном выполнении цепочки действий.",
    "AI safety и надежность": "Надежность и безопасность AI все сильнее становятся частью самого продукта, а не отдельной проверки в конце.",
    "поиск и работа с информацией": "Качество AI все чаще упирается не только в модель, но и в то, как она ищет и использует информацию.",
    "AI в медицине": "AI в медицине движется в сторону более понятных и прикладных сценариев, но требует особенно осторожной оценки.",
    "AI в обучении": "Самые интересные AI-идеи для обучения не просто отвечают, а помогают человеку реально понять материал.",
    "AI для изображений": "Ценность AI для изображений растет там, где он помогает решать конкретную задачу, а не только впечатляет качеством картинки.",
    "AI для видео": "AI для видео становится интереснее тогда, когда улучшает не только генерацию, но и реальный рабочий процесс.",
    "AI для аудио": "Будущее AI для аудио зависит от того, насколько надежно он работает на живой речи и шумных данных.",
    "голосовые AI-сценарии": "Голосовой AI становится по-настоящему полезным только тогда, когда его удобно и безопасно использовать в реальном диалоге.",
    "multimodal AI": "Следующий шаг для multimodal AI — не просто видеть и слышать, а связывать это в полезное действие.",
    "языковые модели": "Для обычного пользователя важнее не размер модели, а то, насколько она помогает в конкретной задаче.",
    "AI для работы и productivity": "Лучшие productivity-сценарии AI — те, что снимают рутину, а не добавляют новый слой сложности.",
    "рекомендательные AI-системы": "Хорошие рекомендательные системы ценны тогда, когда помогают выбрать нужное, а не просто удерживают внимание.",
    "прикладной AI": "Практическая ценность AI лучше всего видна там, где идею можно быстро связать с понятной задачей пользователя.",
}

CATEGORY_LABELS = {
    "cs.AI": "AI",
    "cs.LG": "ML",
    "cs.CL": "NLP",
    "cs.CV": "CV",
    "stat.ML": "StatML",
}

CONTRIBUTION_HINTS = [
    ("framework", "предлагают структуру решения для практического использования"),
    ("architecture", "предлагают структуру решения для практического использования"),
    ("system", "собирают прикладную систему под конкретный сценарий"),
    ("benchmark", "сравнивают подходы и проверяют, что работает лучше"),
    ("evaluate", "сравнивают подходы и проверяют, что работает лучше"),
    ("evaluation", "сравнивают подходы и проверяют, что работает лучше"),
    ("safety", "проверяют, насколько надежно это работает в реальных сценариях"),
    ("accuracy", "смотрят, где система становится точнее, а где у нее остаются слабые места"),
    ("dataset", "собирают основу для обучения и сравнения новых систем"),
    ("corpus", "собирают основу для обучения и сравнения новых систем"),
    ("agent", "показывают, как агентный подход можно использовать на практике"),
    ("assistant", "показывают, как AI может быть полезнее как помощник"),
    ("survey", "делают обзор направления"),
    ("review", "делают обзор направления"),
]

ARTIFACT_HINTS = [
    ("assistant", "AI-ассистента"),
    ("agent", "AI-агента"),
    ("framework", "фреймворк"),
    ("architecture", "архитектуру"),
    ("system", "систему"),
    ("model", "модель"),
    ("models", "модель"),
    ("benchmark", "benchmark"),
    ("dataset", "набор данных"),
    ("interface", "интерфейс"),
    ("workflow", "рабочий сценарий"),
]

TITLE_TOPIC_HINTS = [
    ("symptom", "оценка симптомов"),
    ("clinical", "клинические сценарии"),
    ("medical", "медицинские сценарии"),
    ("health", "здоровье"),
    ("search", "поиск информации"),
    ("retrieval", "поиск и отбор данных"),
    ("audio-visual", "работа со звуком и изображением"),
    ("multimodal", "работа с несколькими типами данных"),
    ("video", "работа с видео"),
    ("audio", "работа со звуком"),
    ("image", "работа с изображениями"),
    ("voice", "голосовые сценарии"),
    ("reasoning", "пошаговые рассуждения"),
    ("red team", "поиск уязвимостей AI"),
    ("red teaming", "поиск уязвимостей AI"),
    ("safety", "безопасность AI"),
    ("benchmark", "сравнение подходов"),
    ("education", "обучение"),
    ("recommendation", "рекомендации"),
]

THEME_TITLE_PREFIX = {
    "AI-ассистенты": "AI-ассистент",
    "AI-агенты": "AI-агент",
    "AI safety и надежность": "Надежность AI",
    "поиск и работа с информацией": "AI для поиска",
    "AI в медицине": "AI в медицине",
    "AI в обучении": "AI для обучения",
    "AI для изображений": "AI для изображений",
    "AI для видео": "AI для видео",
    "AI для аудио": "AI для аудио",
    "голосовые AI-сценарии": "Голосовой AI",
    "multimodal AI": "Multimodal AI",
    "языковые модели": "Языковые модели",
    "AI для работы и productivity": "AI для работы",
    "рекомендательные AI-системы": "AI-рекомендации",
    "прикладной AI": "Прикладной AI",
}

ACTION_HINTS = [
    ("red team", "находить уязвимости и слабые места до того, как они проявятся в продукте"),
    ("red teaming", "находить уязвимости и слабые места до того, как они проявятся в продукте"),
    ("security", "лучше защищаться от уязвимостей и опасных сценариев"),
    ("adversarial", "лучше защищаться от уязвимостей и опасных сценариев"),
    ("jailbreak", "лучше защищаться от уязвимостей и опасных сценариев"),
    ("safety", "работать надежнее и безопаснее в реальных сценариях"),
    ("symptom", "лучше разбирать симптомы и помогать в первичной оценке состояния"),
    ("medical", "аккуратнее работать в медицинских сценариях"),
    ("clinical", "надежнее работать в медицинских сценариях"),
    ("health", "быть полезнее в задачах, связанных со здоровьем"),
    ("audio-visual", "одновременно понимать звук и изображение"),
    ("multimodal", "одновременно работать с несколькими типами данных"),
    ("audio", "лучше работать со звуком и речью"),
    ("video", "лучше понимать и обрабатывать видео"),
    ("image", "лучше понимать или создавать изображения"),
    ("search", "лучше искать и отбирать нужную информацию"),
    ("retrieval", "лучше находить нужные данные и контекст"),
    ("agent", "самостоятельнее выполнять цепочки действий"),
    ("assistant", "быть полезнее как цифровой помощник"),
    ("reasoning", "лучше рассуждать по шагам"),
    ("workflow", "удобнее автоматизировать рабочие задачи"),
    ("education", "лучше помогать в обучении"),
    ("recommendation", "точнее подбирать полезные рекомендации"),
]


def _article_text(scored_article: ScoredArticle) -> str:
    return f"{scored_article.article.title} {scored_article.article.summary}".lower()


def _detect_action_hint(scored_article: ScoredArticle) -> str:
    text = _article_text(scored_article)
    for keyword, hint in ACTION_HINTS:
        if keyword in text:
            return hint
    return "лучше решать прикладные задачи, понятные обычному пользователю"


def _detect_contribution_hint(scored_article: ScoredArticle) -> str:
    text = _article_text(scored_article)
    for keyword, hint in CONTRIBUTION_HINTS:
        if keyword in text:
            return hint
    return "предлагают прикладной подход и показывают, где он может быть полезен"


def _format_date(raw_value: str) -> str:
    if not raw_value:
        return ""

    try:
        return datetime.fromisoformat(raw_value.replace("Z", "+00:00")).strftime("%d.%m.%Y")
    except ValueError:
        return raw_value[:10]


def _format_authors(authors: list[str]) -> str:
    if not authors:
        return "Авторы не указаны"
    if len(authors) == 1:
        return authors[0]
    if len(authors) == 2:
        return f"{authors[0]}, {authors[1]}"
    return f"{authors[0]} и еще {len(authors) - 1}"


def _format_categories(categories: list[str]) -> str:
    labels = [CATEGORY_LABELS.get(category, category) for category in categories[:3]]
    return ", ".join(labels)


def _detect_artifact(scored_article: ScoredArticle) -> str:
    text = _article_text(scored_article)
    for keyword, artifact in ARTIFACT_HINTS:
        if keyword in text:
            return artifact
    return "подход"


def _detect_title_topic(scored_article: ScoredArticle) -> str:
    title_text = scored_article.article.title.lower()
    summary_text = scored_article.article.summary.lower()

    return detect_title_topic_from_text(title_text, summary_text)


def detect_title_topic_from_text(title_text: str, summary_text: str = "") -> str:
    for keyword, topic in TITLE_TOPIC_HINTS:
        if keyword in title_text:
            return topic

    for keyword, topic in TITLE_TOPIC_HINTS:
        if keyword in summary_text:
            return topic

    return "практическое применение"


def _build_russian_title(scored_article: ScoredArticle) -> str:
    return build_russian_title_from_text(
        theme=scored_article.theme,
        title_text=scored_article.article.title,
        summary_text=scored_article.article.summary,
    )


def build_russian_title_from_text(
    theme: str,
    title_text: str,
    summary_text: str = "",
) -> str:
    theme_prefix = THEME_TITLE_PREFIX.get(theme, THEME_TITLE_PREFIX["прикладной AI"])
    topic = detect_title_topic_from_text(title_text.lower(), summary_text.lower())

    if theme == "AI в медицине":
        return f"{theme_prefix}: {topic}"

    if theme == "AI safety и надежность":
        return f"{theme_prefix}: {topic}"

    return f"{theme_prefix}: {topic}"


def _build_general_description(
    scored_article: ScoredArticle,
    action_hint: str,
    contribution_hint: str,
    artifact: str,
) -> str:
    theme = scored_article.theme
    if "обзор направления" in contribution_hint:
        return (
            f"Авторы разбирают, как сейчас развивается {theme.lower()}, "
            f"и на что стоит обратить внимание в этом направлении."
        )

    if artifact == "подход":
        templates = (
            "Авторы показывают новый подход, который помогает AI {action_hint}.",
            "В статье описан подход, который помогает AI {action_hint}.",
            "Работа предлагает подход, который помогает AI {action_hint}.",
        )
        index = _variant_index(scored_article.article.arxiv_id, len(templates))
        return templates[index].format(action_hint=action_hint)

    index = _variant_index(scored_article.article.arxiv_id, len(GENERAL_DESCRIPTION_TEMPLATES))
    return GENERAL_DESCRIPTION_TEMPLATES[index].format(
        artifact=artifact,
        action_hint=action_hint,
    )


def _variant_index(seed: str, count: int) -> int:
    return sum(ord(char) for char in seed) % count


def _sentence_case(text: str) -> str:
    if not text:
        return text
    return text[0].upper() + text[1:]


def _recommendation_variant(text: str, seed: str) -> str:
    normalized = text.lower()
    existing_prefixes = (
        "стоит ",
        "полезно ",
        "имеет смысл ",
        "важно",
        "обращайте внимание",
    )
    if normalized.startswith(existing_prefixes):
        return text

    index = _variant_index(seed, len(RECOMMENDATION_PREFIXES))
    return f"{RECOMMENDATION_PREFIXES[index]} {text[0].lower() + text[1:]}"


def _build_post_content(scored_article: ScoredArticle) -> dict[str, str]:
    theme = scored_article.theme
    action_hint = _detect_action_hint(scored_article)
    contribution_hint = _detect_contribution_hint(scored_article)
    artifact = _detect_artifact(scored_article)
    general_description = _build_general_description(
        scored_article=scored_article,
        action_hint=action_hint,
        contribution_hint=contribution_hint,
        artifact=artifact,
    )

    index = _variant_index(scored_article.article.arxiv_id, len(WHAT_DONE_TEMPLATES))
    what_happened = WHAT_DONE_TEMPLATES[index].format(
        contribution_hint=contribution_hint,
        action_hint=action_hint,
    )
    problems = _sentence_case(THEME_PROBLEMS.get(theme, THEME_PROBLEMS["прикладной AI"]))
    use_cases = _sentence_case(THEME_USE_CASES.get(theme, THEME_USE_CASES["прикладной AI"]))
    recommendation = _recommendation_variant(
        THEME_RECOMMENDATIONS.get(
        theme,
        THEME_RECOMMENDATIONS["прикладной AI"],
        ),
        scored_article.article.arxiv_id,
    )
    conclusion = THEME_CONCLUSIONS.get(theme, THEME_CONCLUSIONS["прикладной AI"])
    return {
        "theme": theme,
        "russian_title": _build_russian_title(scored_article),
        "general_description": general_description,
        "what_happened": what_happened,
        "problems": problems,
        "use_cases": use_cases,
        "recommendation": recommendation,
        "conclusion": conclusion,
        "authors": _format_authors(scored_article.article.authors),
        "categories": _format_categories(scored_article.article.categories),
        "published": _format_date(scored_article.article.published),
    }


def format_post(scored_article: ScoredArticle) -> str:
    article = scored_article.article
    content = _build_post_content(scored_article)

    title = html.escape(article.title)
    russian_title = html.escape(content["russian_title"])
    general_description = html.escape(content["general_description"])
    what_happened = html.escape(content["what_happened"])
    problems = html.escape(content["problems"])
    use_cases = html.escape(content["use_cases"])
    recommendation = html.escape(content["recommendation"])
    conclusion = html.escape(content["conclusion"])
    authors = html.escape(content["authors"])
    categories = html.escape(content["categories"])
    published = html.escape(content["published"])
    link = html.escape(article.abs_url)
    pdf_link = html.escape(article.pdf_url) if article.pdf_url else ""

    links = f"<a href=\"{link}\">arXiv</a>"
    if pdf_link:
        links += f" | <a href=\"{pdf_link}\">PDF</a>"

    details = f"{authors} | {categories} | {published}"

    return (
        f"<b>{russian_title}</b>\n"
        f"<i>{title}</i>\n\n"
        f"{general_description}\n\n"
        f"<b>Что сделали:</b> {what_happened}\n\n"
        f"<b>Какие проблемы решает:</b> {problems}\n\n"
        f"<b>Где пригодится:</b> {use_cases}\n\n"
        f"<b>Рекомендация:</b> {recommendation}\n\n"
        f"<b>Вывод:</b> {conclusion}\n\n"
        f"<b>Детали:</b> {details}\n\n"
        f"{links}"
    )
