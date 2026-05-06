from __future__ import annotations

import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass


ARXIV_API_URL = "https://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


@dataclass(frozen=True)
class Article:
    arxiv_id: str
    title: str
    summary: str
    published: str
    updated: str
    categories: list[str]
    authors: list[str]
    abs_url: str
    pdf_url: str


def _build_query(categories: list[str]) -> str:
    return " OR ".join(f"cat:{category}" for category in categories)


def _clean_text(text: str | None) -> str:
    if not text:
        return ""
    return " ".join(text.split())


def _extract_arxiv_id(entry_id: str) -> str:
    return entry_id.rstrip("/").split("/")[-1]


def _to_https(url: str) -> str:
    return url.replace("http://", "https://", 1)


def fetch_recent_articles(categories: list[str], max_results: int) -> list[Article]:
    query = _build_query(categories)
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(params)}"

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ArxivTelegramDigest/1.0 (educational project)"},
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read()

    root = ET.fromstring(payload)
    entries = root.findall("atom:entry", ATOM_NS)
    articles: list[Article] = []

    for entry in entries:
        entry_id = _clean_text(entry.findtext("atom:id", default="", namespaces=ATOM_NS))
        title = _clean_text(entry.findtext("atom:title", default="", namespaces=ATOM_NS))
        summary = _clean_text(entry.findtext("atom:summary", default="", namespaces=ATOM_NS))
        published = _clean_text(
            entry.findtext("atom:published", default="", namespaces=ATOM_NS)
        )
        updated = _clean_text(
            entry.findtext("atom:updated", default="", namespaces=ATOM_NS)
        )

        authors = [
            _clean_text(author.findtext("atom:name", default="", namespaces=ATOM_NS))
            for author in entry.findall("atom:author", ATOM_NS)
        ]

        categories = [
            category.attrib.get("term", "").strip()
            for category in entry.findall("atom:category", ATOM_NS)
            if category.attrib.get("term")
        ]

        pdf_url = ""
        for link in entry.findall("atom:link", ATOM_NS):
            if link.attrib.get("title") == "pdf":
                pdf_url = link.attrib.get("href", "").strip()
                break

        articles.append(
            Article(
                arxiv_id=_extract_arxiv_id(entry_id),
                title=title,
                summary=summary,
                published=published,
                updated=updated,
                categories=categories,
                authors=[author for author in authors if author],
                abs_url=_to_https(entry_id),
                pdf_url=_to_https(pdf_url) if pdf_url else "",
            )
        )

    # arXiv просит не частить с запросами; одной паузы достаточно для локального цикла разработки.
    time.sleep(3)
    return articles
