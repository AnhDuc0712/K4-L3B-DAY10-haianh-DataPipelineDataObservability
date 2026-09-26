from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from core.utils import write_json


def corrupt_clean_dataframe(df: pd.DataFrame, output_log_path) -> pd.DataFrame:
    """TODO(student): simulate nhieu dang data corruption.

    Pseudo-code:
    1. Drop mot so latest records.
    2. Blank summary o mot so dong.
    3. Inject noise vao text.
    4. Lam title bi truncate.
    5. Lam published date cu di.
    6. Add duplicate rows.
    7. Rebuild `text_for_embedding`.
    8. Ghi corruption log vao output_log_path.
    """
    corrupted = df.copy(deep=True)
    logs: list[dict] = []

    def log(kind: str, rows: list[dict]) -> None:
        logs.append({"type": kind, "rows": rows})

    dates = pd.to_datetime(corrupted.get("published"), errors="coerce")
    drop_count = max(1, int(len(corrupted) * 0.2)) if len(corrupted) else 0
    newest = dates.sort_values(ascending=False, kind="mergesort").index[:drop_count]
    dropped = [
        {"index": int(index), "paper_id": str(corrupted.at[index, "paper_id"])}
        for index in newest
    ]
    corrupted = corrupted.drop(index=newest).copy()
    log("drop_latest_20_percent", dropped)

    available = list(corrupted.index)
    summary_indices = [index for index in available if str(corrupted.at[index, "summary"]).strip()]
    blank_index = summary_indices[0] if summary_indices else None
    if blank_index is not None:
        old = str(corrupted.at[blank_index, "summary"])
        corrupted.at[blank_index, "summary"] = ""
        log("blank_summary", [{"index": int(blank_index), "old": old, "new": ""}])
    else:
        log("blank_summary", [])

    noise_index = next((index for index in summary_indices if index != blank_index), None)
    if noise_index is not None:
        old = str(corrupted.at[noise_index, "summary"])
        new = f"{old} [CORRUPTED_NOISE_@@@]"
        corrupted.at[noise_index, "summary"] = new
        log("summary_noise", [{"index": int(noise_index), "old": old, "new": new}])
    else:
        log("summary_noise", [])

    title_index = next(
        (index for index in available if len(str(corrupted.at[index, "title"])) >= 8), None
    )
    if title_index is not None:
        old = str(corrupted.at[title_index, "title"])
        new = old[:7]
        corrupted.at[title_index, "title"] = new
        log("truncate_title_under_8", [{"index": int(title_index), "old": old, "new": new}])
    else:
        log("truncate_title_under_8", [])

    date_index = next((index for index in available if pd.notna(dates.get(index))), None)
    if date_index is not None:
        old = str(corrupted.at[date_index, "published"])
        new_date = pd.Timestamp(corrupted.at[date_index, "published"]) - pd.Timedelta(days=365)
        new = new_date.strftime("%Y-%m-%d")
        corrupted.at[date_index, "published"] = new
        if "age_days" in corrupted:
            corrupted.at[date_index, "age_days"] = corrupted.at[date_index, "age_days"] + 365
        log("date_shift_back_365_days", [{"index": int(date_index), "old": old, "new": new}])
    else:
        log("date_shift_back_365_days", [])

    duplicate_index = available[0] if available else None
    if duplicate_index is not None:
        duplicate = corrupted.loc[[duplicate_index]].copy()
        corrupted = pd.concat([corrupted, duplicate], ignore_index=True)
        log(
            "duplicate_row",
            [{"source_index": int(duplicate_index), "paper_id": str(duplicate.iloc[0]["paper_id"])}],
        )
    else:
        log("duplicate_row", [])

    if "summary_chars" in corrupted:
        corrupted["summary_chars"] = corrupted["summary"].fillna("").astype(str).str.len()
    if "text_for_embedding" in corrupted.columns:
        corrupted["text_for_embedding"] = corrupted.apply(
            lambda row: "\n".join(
                [
                    f"Title: {row.get('title', '')}",
                    f"Authors: {row.get('authors_joined', '')}",
                    f"Published: {row.get('published', '')}",
                    f"Categories: {row.get('categories_joined', '')}",
                    f"Summary: {row.get('summary', '')}",
                ]
            ),
            axis=1,
        )
    write_json(Path(output_log_path), {"corruptions": logs, "input_rows": len(df), "output_rows": len(corrupted)})
    return corrupted.reset_index(drop=True)


def repair_from_raw_snapshot(raw_path, run_date: datetime | None = None) -> pd.DataFrame:
    """Rebuild the clean dataframe from the trusted raw records snapshot."""
    from ingestion.cleaning import build_clean_dataframe
    from ingestion.crossref import load_raw_records

    records = load_raw_records(Path(raw_path))
    return build_clean_dataframe(records, run_date or datetime.now(UTC))
