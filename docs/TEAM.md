# Danh sách thành viên và phân công nhóm

- **Tên nhóm:** `haianh`
- **Khóa/lớp:** `K4-L3B`
- **Repository:** `https://github.com/AnhDuc0712/K4-L3B-DAY10-haianh-DataPipelineDataObservability`
- **Ngày cập nhật:** `2026-09-26`

## Thành viên

| STT | Họ và tên | MSSV | Vai trò chính | Phạm vi phụ trách | Báo cáo cá nhân |
|---:|---|---|---|---|---|
| 1 | Tô Anh Đức | 2A202602639 | Pipeline integration, observability và dashboard | `phase1.py`, `corruption_flow.py`, `quality.py`, `reporting.py`, `app.py` | [`group_report.md`](../report/group_report.md) *(phần phân công và artifact chung)* |
| 2 | Vũ Bá Anh | 2A202602893 | Data foundation, RAG và evaluation | `crossref.py`, `cleaning.py`, `retrieval/`, `testset.py`, metrics và raw/clean artifacts | [`individual_2A202602893_Vũ Bá Anh_report.md`](<../report/individual_2A202602893_Vũ Bá Anh_report.md>) |

## Phân công và output

### Tô Anh Đức — 2A202602639

- **Phạm vi:** Pipeline orchestration, quality/freshness checks, reporting và dashboard.
- **Output:** Baseline/corrupted/repaired flow, quality reports, comparison report và dashboard integration.
- **Artifact chính:** `data/reports/phase1_report.md`, `data/reports/corruption_report.md`, `data/quality/`.

### Vũ Bá Anh — 2A202602893

- **Phạm vi:** Crossref ingestion, cleaning/data contract, retrieval/indexing và evaluation.
- **Output:** Raw records, clean dataset, ChromaDB/embedding artifacts, test set và metrics.
- **Artifact chính:** `data/raw/`, `data/clean/`, `data/embeddings/`, `data/eval/test_set.json`, `data/results/*_metrics.json`.

## Luồng dữ liệu chung

```text
Crossref API/snapshot
  -> PaperRecord và raw lineage
  -> cleaning, age_days, text_for_embedding
  -> embeddings và ChromaDB
  -> baseline evaluation
  -> quality/freshness gate
  -> corruption
  -> corrupted evaluation
  -> repair từ raw snapshot
  -> repaired evaluation và comparison report
```

## Kết quả đã xác minh

| Metric | Baseline | Corrupted | Repaired |
|---|---:|---:|---:|
| Retrieval Hit Rate | 1.0 | 0.0 | 1.0 |
| Mean Token F1 | 1.0 | 0.7246 | 1.0 |
| Judge Accuracy | 1.0 | 0.8 | 1.0 |
| Mean Judge Score | 5.0 | 3.6 | 5.0 |
| Quality gate | PASS | FAIL | PASS |
| Freshness | FRESH, 1/24 stale | FRESH, 3/21 stale | FRESH, 1/24 stale |

Các số liệu trên được đọc từ:

- `data/results/baseline_metrics.json`
- `data/results/corrupted_metrics.json`
- `data/results/repaired_metrics.json`
- `data/quality/baseline_quality_report.json`
- `data/quality/corrupted_quality_report.json`

## Lệnh tái hiện

```powershell
python script/run_phase1.py
python script/run_corruption_flow.py
```

Ragas chưa chạy vì chưa bật `RUN_RAGAS=1`; các metrics nêu trên là kết quả thực tế của các evaluation run đã hoàn tất.
