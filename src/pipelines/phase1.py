from __future__ import annotations

from datetime import UTC, datetime

from core.config import Settings, load_settings
from core.utils import write_csv, write_json
from evaluation.metrics import evaluate_pipeline
from evaluation.testset import build_test_set
from ingestion.cleaning import build_clean_dataframe
from ingestion.crossref import fetch_source_records, load_raw_records
from observability.quality import run_data_quality_checks
from observability.reporting import generate_phase1_report
from retrieval.index import LocalEmbeddingIndex


def run_phase1_pipeline(settings: Settings) -> dict:
    """Run ingestion, cleaning, indexing, evaluation, quality, and reporting."""
    records = (
        fetch_source_records(settings)
        if settings.refresh_source or not settings.paths.raw_records_json.exists()
        else load_raw_records(settings.paths.raw_records_json)
    )
    df = build_clean_dataframe(records, datetime.now(UTC))
    write_csv(df, settings.paths.clean_csv)
    write_json(settings.paths.clean_json, df.to_dict(orient="records"))

    index = LocalEmbeddingIndex.build(df, settings, settings.paths.embeddings_json)
    test_set = build_test_set(df, settings.paths.eval_testset)
    bundle = evaluate_pipeline(
        settings,
        index,
        settings.paths.eval_testset,
        settings.paths.baseline_metrics,
        settings.paths.baseline_answers,
    )
    quality = run_data_quality_checks(df, settings, "baseline")
    write_json(settings.paths.baseline_quality_report, quality)
    generate_phase1_report(
        settings.paths.baseline_report,
        {
            "source": settings.source_api,
            "records": len(records),
            "clean_rows": len(df),
            "test_questions": len(test_set),
        },
        bundle.summary,
        quality,
        quality["freshness"],
    )
    if not quality["success"]:
        raise RuntimeError("Baseline quality gate failed")
    return {"metrics": bundle.summary, "quality": quality, "rows": len(df)}

def main() -> None:
    """TODO(student): xay dung baseline pipeline end-to-end.

    Pseudo-code:
    1. Load settings.
    2. Load hoac fetch raw records.
    3. Clean data.
    4. Save clean CSV/JSON.
    5. Build Chroma index.
    6. Tao hoac load evaluation set.
    7. Evaluate.
    8. Run quality checks va freshness report.
    9. Tao markdown report.
    10. Co the demo agent tren vai sample question.
    """
    run_phase1_pipeline(load_settings())
