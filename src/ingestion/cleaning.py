from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
import html
import re

import pandas as pd

from core.utils import normalize_whitespace
from ingestion.crossref import PaperRecord


def build_clean_dataframe(records: list[PaperRecord], run_date: datetime) -> pd.DataFrame:
    """TODO(student): clean raw records thanh dataframe san sang de embed.

    Pseudo-code:
    1. Normalize title, summary, authors, categories.
    2. Parse published/updated date.
    3. Tinh age_days.
    4. Tao cot helper:
       - authors_joined
       - categories_joined
       - summary_chars
       - text_for_embedding
    5. Drop duplicates va filter row xau.
    6. Sort dataframe va return.
    """
    def clean_text(value: object) -> str:
        value = "" if value is None else str(value)
        value = html.unescape(re.sub(r"<[^>]*>", " ", value))
        return re.sub(r"\s+([,.;:!?])", r"\1", normalize_whitespace(value))

    def clean_list(value: object) -> list[str]:
        values = value if isinstance(value, list) else [value]
        return [item for item in (clean_text(item) for item in values) if item]

    rows = []
    for record in records:
        row = asdict(record)
        row["paper_id"] = clean_text(row.get("paper_id"))
        row["title"] = clean_text(row.get("title"))
        row["summary"] = clean_text(row.get("summary"))
        row["authors"] = clean_list(row.get("authors"))
        row["categories"] = clean_list(row.get("categories"))
        row["published"] = clean_text(row.get("published"))
        row["updated"] = clean_text(row.get("updated"))
        row["abs_url"] = clean_text(row.get("abs_url"))
        row["pdf_url"] = clean_text(row.get("pdf_url"))
        row["comment"] = clean_text(row.get("comment"))
        row["authors_joined"] = ", ".join(row["authors"])
        row["categories_joined"] = ", ".join(row["categories"])
        rows.append(row)

    columns = [
        "paper_id", "title", "summary", "authors", "categories", "primary_category",
        "published", "updated", "abs_url", "pdf_url", "comment",
    ]
    df = pd.DataFrame(rows, columns=columns + ["authors_joined", "categories_joined"])
    if df.empty:
        df["summary_chars"] = pd.Series(dtype="int64")
        df["age_days"] = pd.Series(dtype="float64")
        df["text_for_embedding"] = pd.Series(dtype="object")
        return df

    df = df[df["paper_id"].ne("") & df["title"].ne("")].drop_duplicates("paper_id", keep="first").copy()
    published_dates = pd.to_datetime(df["published"], errors="coerce", utc=True)
    run_timestamp = pd.Timestamp(run_date)
    run_timestamp = run_timestamp.tz_localize("UTC") if run_timestamp.tzinfo is None else run_timestamp.tz_convert("UTC")
    df["published"] = published_dates.dt.strftime("%Y-%m-%d").fillna("")
    df["age_days"] = (run_timestamp - published_dates).dt.days
    df["summary_chars"] = df["summary"].str.len()
    df["text_for_embedding"] = df.apply(
        lambda row: "\n".join(
            [
                f"Title: {row['title']}",
                f"Authors: {row['authors_joined']}",
                f"Published: {row['published']}",
                f"Categories: {row['categories_joined']}",
                f"Summary: {row['summary']}",
            ]
        ),
        axis=1,
    )
    return df.sort_values(["published", "paper_id"], ascending=[False, True], na_position="last").reset_index(drop=True)
