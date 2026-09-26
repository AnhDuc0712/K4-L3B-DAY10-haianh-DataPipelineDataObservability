from __future__ import annotations

from typing import Any

import great_expectations as gx
import pandas as pd
from great_expectations.core import ExpectationSuite
from great_expectations.expectations import (
    ExpectColumnValueLengthsToBeBetween,
    ExpectColumnValuesToBeUnique,
    ExpectColumnValuesToNotBeNull,
    ExpectTableRowCountToBeBetween,
)

from core.config import Settings


def evaluate_freshness_sla(
    df: pd.DataFrame, threshold_days: int = 180, max_stale_ratio: float = 0.25
) -> dict[str, Any]:
    """Evaluate the freshness SLA from the dataframe's age_days column."""
    ages = pd.to_numeric(df.get("age_days", pd.Series(dtype="float64")), errors="coerce")
    stale_rows = int((ages > threshold_days).sum())
    total_rows = len(df)
    stale_ratio = stale_rows / total_rows if total_rows else 0.0
    return {
        "threshold_days": threshold_days,
        "max_stale_ratio": max_stale_ratio,
        "stale_rows": stale_rows,
        "total_rows": total_rows,
        "stale_ratio": stale_ratio,
        "is_fresh": stale_ratio <= max_stale_ratio,
    }


def run_data_quality_checks(df: pd.DataFrame, settings: Settings, report_name: str) -> dict[str, Any]:
    """TODO(student): tao bo data quality checks.

    Pseudo-code:
    1. Check row count.
    2. Check `paper_id` not null va unique.
    3. Check `title` not null.
    4. Check do dai `summary`.
    5. Check freshness bang `age_days`.
    6. Ghi ket qua vao `data/quality/`.
    """
    context = gx.get_context(mode="ephemeral")
    data_source = context.data_sources.add_pandas(name="papers_source")
    data_asset = data_source.add_dataframe_asset(name="papers_asset")
    batch_definition = data_asset.add_batch_definition_whole_dataframe("papers_batch")
    batch = batch_definition.get_batch(batch_parameters={"dataframe": df})

    suite = ExpectationSuite(name=f"{report_name}_quality")
    suite.add_expectation(ExpectTableRowCountToBeBetween(min_value=1, max_value=55000))
    for column in ("paper_id", "title", "text_for_embedding"):
        suite.add_expectation(ExpectColumnValuesToNotBeNull(column=column))
    suite.add_expectation(ExpectColumnValuesToBeUnique(column="paper_id"))
    suite.add_expectation(
        ExpectColumnValueLengthsToBeBetween(column="summary", min_value=30, max_value=None)
    )

    validation = batch.validate(suite)
    validation_result = validation.to_json_dict()
    freshness = evaluate_freshness_sla(df, settings.freshness_threshold_days)
    return {
        "success": bool(validation_result.get("success")) and freshness["is_fresh"],
        "stage": report_name,
        "expectations": validation_result.get("results", []),
        "freshness": freshness,
    }


def build_freshness_report(df: pd.DataFrame, settings: Settings, report_path) -> dict[str, Any]:
    """TODO(student): tong hop freshness report.

    Pseudo-code:
    1. Tim latest va oldest published date.
    2. Dem so dong stale.
    3. Tao payload:
       - latest_published
       - oldest_published
       - stale_rows
       - total_rows
       - is_fresh
    4. Ghi JSON report.
    """
    raise NotImplementedError("Student task: implement freshness reporting.")
