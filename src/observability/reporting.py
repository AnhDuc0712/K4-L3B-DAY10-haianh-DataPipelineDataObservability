from __future__ import annotations

from typing import Any

from core.utils import write_text


def generate_phase1_report(
    report_path,
    source_summary: dict[str, Any],
    metrics: dict[str, Any],
    quality: dict[str, Any],
    freshness: dict[str, Any],
) -> None:
    """TODO(student): viet markdown report cho baseline phase.

    Pseudo-code:
    1. Gom source summary.
    2. In metrics retrieval/evaluation.
    3. In data quality va freshness.
    4. Ghi markdown vao report_path.
    """
    lines = [
        "# Phase 1 Baseline Report",
        "",
        "## Source and data",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Source | {source_summary.get('source', '')} |",
        f"| Ingested records | {source_summary.get('records', 0)} |",
        f"| Clean rows | {source_summary.get('clean_rows', 0)} |",
        f"| Test questions | {source_summary.get('test_questions', 0)} |",
        "",
        "## Baseline metrics",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Retrieval Hit Rate | {metrics.get('retrieval_hit_rate', 0.0):.4f} |",
        f"| Mean Token F1 | {metrics.get('mean_token_f1', 0.0):.4f} |",
        f"| Judge Accuracy | {metrics.get('judge_accuracy', 0.0):.4f} |",
        f"| Mean Judge Score | {metrics.get('mean_judge_score', 0.0):.4f} |",
        "",
        "## Quality gate",
        "",
        f"- Success: `{quality.get('success', False)}`",
        f"- Expectations: `{len(quality.get('expectations', []))}`",
        f"- Freshness: `{freshness.get('is_fresh', False)}`",
        f"- Stale rows: `{freshness.get('stale_rows', 0)}` / `{freshness.get('total_rows', 0)}`",
        f"- Stale ratio: `{freshness.get('stale_ratio', 0.0):.4f}`",
        "",
    ]
    write_text(report_path, "\n".join(lines))


def generate_corruption_report(
    report_path,
    baseline_metrics: dict[str, Any],
    corrupted_metrics: dict[str, Any],
    repaired_metrics: dict[str, Any],
    corrupted_quality: dict[str, Any],
    repaired_quality: dict[str, Any],
    corrupted_freshness: dict[str, Any],
    repaired_freshness: dict[str, Any],
) -> None:
    """TODO(student): viet markdown report so sanh baseline/corrupted/repaired."""
    metric_names = (
        ("Retrieval Hit Rate", "retrieval_hit_rate"),
        ("Mean Token F1", "mean_token_f1"),
        ("Judge Accuracy", "judge_accuracy"),
        ("Mean Judge Score", "mean_judge_score"),
    )
    lines = [
        "# Corruption and Repair Report",
        "",
        "## Baseline vs Corrupted vs Repaired",
        "",
        "| Metric | Baseline | Corrupted | Repaired |",
        "|---|---:|---:|---:|",
    ]
    for label, key in metric_names:
        lines.append(
            f"| {label} | {baseline_metrics.get(key, 0.0):.4f} | "
            f"{corrupted_metrics.get(key, 0.0):.4f} | {repaired_metrics.get(key, 0.0):.4f} |"
        )
    lines.extend(
        [
            "",
            "## Quality and freshness",
            "",
            "| Signal | Corrupted | Repaired |",
            "|---|---:|---:|",
            f"| Quality gate | {corrupted_quality.get('success', False)} | {repaired_quality.get('success', False)} |",
            f"| Freshness | {corrupted_freshness.get('is_fresh', False)} | {repaired_freshness.get('is_fresh', False)} |",
            f"| Stale ratio | {corrupted_freshness.get('stale_ratio', 0.0):.4f} | {repaired_freshness.get('stale_ratio', 0.0):.4f} |",
            "",
            "Metrics above are measured from each corresponding index and evaluation run.",
        ]
    )
    write_text(report_path, "\n".join(lines))
