from __future__ import annotations

from dataclasses import dataclass
import html
import json
from pathlib import Path
import re

import requests

from core.config import Settings
from core.utils import normalize_whitespace, read_json, write_json


@dataclass(frozen=True)
class PaperRecord:
    paper_id: str
    title: str
    summary: str
    authors: list[str]
    categories: list[str]
    primary_category: str
    published: str
    updated: str
    abs_url: str
    pdf_url: str
    comment: str


def parse_crossref_payload(payload: dict) -> list[PaperRecord]:
    """TODO(student): parse Crossref payload thanh list PaperRecord.

    Pseudo-code:
    1. Duyet `payload["message"]["items"]`.
    2. Lay DOI, title, abstract, authors, subject, dates, URLs.
    3. Chuan hoa text va bo record khong hop le.
    4. Tra ve list `PaperRecord`.
    """
    message = payload.get("message", {}) if isinstance(payload, dict) else {}
    items = message.get("items", []) if isinstance(message, dict) else []
    if not isinstance(items, list):
        return []

    def text(value: object) -> str:
        if isinstance(value, list):
            value = value[0] if value else ""
        value = normalize_whitespace(re.sub(r"<[^>]*>", " ", html.unescape(str(value or ""))))
        return re.sub(r"\s+([,.;:!?])", r"\1", value)

    def date_value(value: object) -> str:
        parts = value.get("date-parts") if isinstance(value, dict) else None
        parts = parts[0] if isinstance(parts, list) and parts else []
        if not isinstance(parts, list) or not parts or not all(isinstance(part, int) for part in parts):
            return ""
        return "-".join(f"{part:02d}" if index else str(part) for index, part in enumerate(parts))

    records: list[PaperRecord] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        doi = text(item.get("DOI"))
        title = text(item.get("title"))
        if not doi or not title:
            continue
        authors = []
        for author in item.get("author", []) if isinstance(item.get("author", []), list) else []:
            if isinstance(author, dict):
                name = " ".join(part for part in (text(author.get("given")), text(author.get("family"))) if part)
            else:
                name = text(author)
            if name:
                authors.append(name)
        categories = item.get("subject", [])
        categories = categories if isinstance(categories, list) else [categories]
        categories = [text(category) for category in categories if text(category)]
        published = date_value(item.get("published")) or date_value(item.get("published-print"))
        published = published or date_value(item.get("published-online")) or date_value(item.get("issued"))
        updated = date_value(item.get("updated")) or published
        if not updated and isinstance(item.get("created"), dict):
            updated = str(item["created"].get("date-time", ""))[:10]
        url = text(item.get("URL")) or f"https://doi.org/{doi}"
        pdf_url = next(
            (text(link.get("URL")) for link in item.get("link", []) if isinstance(link, dict) and "pdf" in text(link.get("content-type")).lower()),
            url,
        ) if isinstance(item.get("link", []), list) else url
        records.append(PaperRecord(
            paper_id=doi,
            title=title,
            summary=text(item.get("abstract", item.get("summary", ""))),
            authors=authors,
            categories=categories,
            primary_category=categories[0] if categories else "",
            published=published,
            updated=updated,
            abs_url=url,
            pdf_url=pdf_url,
            comment=f"Crossref record {doi}",
        ))
    return records


def fetch_source_records(settings: Settings) -> list[PaperRecord]:
    """TODO(student): goi source API, luu raw response, parse thanh records.

    Pseudo-code:
    1. Tao params tu `settings.source_query`, `settings.source_filter`, `settings.max_results`.
    2. Goi API voi retry cho cac status code nhu 429/503.
    3. Luu raw response vao `settings.paths.raw_api_response`.
    4. Parse payload bang `parse_crossref_payload`.
    5. Luu records vao `settings.paths.raw_records_json`.
    """
    snapshot = settings.paths.raw_api_response

    def from_snapshot() -> list[PaperRecord]:
        if not snapshot.exists():
            raise requests.RequestException("Crossref snapshot is unavailable")
        return parse_crossref_payload(read_json(snapshot))

    try:
        response = requests.get(
            "https://api.crossref.org/works",
            params={
                "query": settings.source_query,
                "filter": settings.source_filter,
                "rows": settings.max_results,
            },
            timeout=30,
        )
    except requests.RequestException:
        records = from_snapshot()
    else:
        if response.status_code == 429:
            records = from_snapshot()
        else:
            response.raise_for_status()
            try:
                payload = response.json()
                records = parse_crossref_payload(payload)
            except (ValueError, json.JSONDecodeError):
                records = from_snapshot()
            if not records:
                records = from_snapshot()
            else:
                write_json(snapshot, payload)
    write_json(settings.paths.raw_records_json, [record.__dict__ for record in records])
    return records


def load_raw_records(path: Path) -> list[PaperRecord]:
    """TODO(student): doc JSON snapshot va map thanh `PaperRecord`."""
    return [PaperRecord(**item) for item in read_json(path) if isinstance(item, dict)]
