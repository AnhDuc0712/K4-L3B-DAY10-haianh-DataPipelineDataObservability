# Corruption and Repair Report

## Baseline vs Corrupted vs Repaired

| Metric | Baseline | Corrupted | Repaired |
|---|---:|---:|---:|
| Retrieval Hit Rate | 1.0000 | 0.0000 | 1.0000 |
| Mean Token F1 | 1.0000 | 0.7246 | 1.0000 |
| Judge Accuracy | 1.0000 | 0.8000 | 1.0000 |
| Mean Judge Score | 5.0000 | 3.6000 | 5.0000 |

## Quality and freshness

| Signal | Corrupted | Repaired |
|---|---:|---:|
| Quality gate | False | True |
| Freshness | True | True |
| Stale ratio | 0.1429 | 0.0417 |

Metrics above are measured from each corresponding index and evaluation run.