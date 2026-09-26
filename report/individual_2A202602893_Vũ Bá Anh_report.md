# Báo cáo cá nhân — Vũ Bá Anh

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
|---|---|
| Họ và tên | Vũ Bá Anh |
| MSSV | 2A202602893 |
| Khóa/Lớp | K4-L3B |
| Tên nhóm | haianh |
| Vai trò chính | Data foundation, RAG và evaluation |
| Repository | https://github.com/AnhDuc0712/K4-L3B-DAY10-haianh-DataPipelineDataObservability |
| Ngày hoàn thành | 2026-09-26 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input | Output | Trạng thái |
|---|---|---|---|---|
| Ingestion Crossref | `src/ingestion/crossref.py` — `parse_crossref_payload`, `fetch_source_records` | Crossref API hoặc snapshot JSON | `data/raw/crossref_response.json`, `crossref_records.json` | Hoàn thành |
| Cleaning và data contract | `src/ingestion/cleaning.py` — `build_clean_dataframe` | `PaperRecord` | `papers_clean.csv/json`, schema clean | Hoàn thành |
| RAG retrieval | `src/retrieval/` | Clean dataframe, câu hỏi truy vấn | Embeddings, ChromaDB collections, search results | Hoàn thành |
| Evaluation set và metrics | `src/evaluation/testset.py`, `metrics.py` | Clean dataframe, index | `test_set.json`, baseline/corrupted/repaired metrics | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
|---|---|---|
| Kiểm tra contract giữa clean dataframe, index và evaluation | Pipeline integration, observability | Ba trạng thái dùng chung schema và evaluation set |
| Kiểm tra raw/clean artifacts phục vụ repair | Corruption flow | Repair rebuild từ raw snapshot, không sửa trực tiếp dữ liệu bẩn |

## 3. Kết quả theo vai trò

| Nhiệm vụ | File/artifact | Kết quả bàn giao | Cách xác minh |
|---|---|---|---|
| Parse và fallback Crossref | `src/ingestion/crossref.py` | 24 `PaperRecord`, hỗ trợ HTML/JATS và fallback snapshot | Raw artifacts có 24 records |
| Chuẩn hóa dữ liệu | `src/ingestion/cleaning.py` | 24 dòng clean, deduplicate theo `paper_id`, có `age_days` và `text_for_embedding` | `data/clean/papers_clean.csv/json` |
| Xây dựng retrieval index | `src/retrieval/index.py`, `embeddings.py` | ChromaDB persistent với `papers-baseline`, `papers-corrupted`, `papers-repaired` | Manifest trong `data/embeddings/` |
| Tạo evaluation set | `src/evaluation/testset.py` | 10 câu hỏi, phân bổ summary/authors/date/categories | `data/eval/test_set.json` |
| Đo baseline và recovery | `src/evaluation/metrics.py` | Hit Rate, Token F1, judge metrics cho ba trạng thái | `data/results/*_metrics.json` |

Test set 10 câu hỏi được dùng chung cho baseline, corrupted và repaired để metrics phản ánh chất lượng dữ liệu/index, không bị trộn với thay đổi câu hỏi hoặc ground truth.

## 4. Giải thích kỹ thuật

### Vấn đề cần giải quyết

Pipeline RAG cần data contract ổn định từ metadata Crossref đến vector index và evaluation. XML trong abstract, ngày không chuẩn hóa hoặc document ID không ổn định đều có thể làm sai retrieval và quality checks.

### Cách triển khai

Crossref được parse thành `PaperRecord` với DOI làm `paper_id`. Parser làm sạch HTML/XML, bao gồm JATS, chuẩn hóa title/summary, ghép tên tác giả và lấy subject làm categories. Khi API lỗi mạng hoặc rate limit, pipeline đọc snapshot local.

Cleaning chuẩn hóa text, chuyển `published` về ISO date, tính `age_days`, loại record thiếu `paper_id`/title và deduplicate theo DOI. Context embedding gồm Title, Authors, Published, Categories và Summary.

Retrieval dùng `sentence-transformers/all-MiniLM-L6-v2` và ChromaDB persistent. Mỗi trạng thái có collection/manifest riêng. Evaluation dùng DOI trong `ground_truth_doc_ids` để tính retrieval Hit Rate, đồng thời tính Token F1 và judge metrics.

### Input, output và contract

| Thành phần | Mô tả |
|---|---|
| Input | Crossref payload/snapshot và danh sách `PaperRecord` |
| Output | Clean dataframe với `paper_id`, text fields, `age_days`, `text_for_embedding` |
| Module phụ thuộc | `core.config`, `core.utils`, pandas, Crossref snapshot |
| Module sử dụng output | `retrieval/index.py`, `evaluation/metrics.py`, quality gate |
| Điều kiện lỗi | API lỗi, field thiếu, XML summary, ngày không hợp lệ, duplicate DOI |

### Cách xác minh

```powershell
python script/run_phase1.py
python script/run_corruption_flow.py
```

- **Kết quả thực tế:** Phase 1 và corruption flow chạy thành công; corrupted quality gate FAIL, repaired quality gate PASS.
- **Artifact/log:** `data/raw/`, `data/clean/`, `data/eval/test_set.json`, `data/embeddings/`, `data/results/`.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Cần so sánh công bằng baseline, corrupted và repaired.
- **Các phương án:** Sinh test set riêng cho từng trạng thái; hoặc giữ một test set và ground truth cố định.
- **Phương án đã chọn:** Dùng chung `data/eval/test_set.json` với DOI trong `ground_truth_doc_ids` cho cả ba trạng thái.
- **Lý do:** Loại bỏ biến động từ evaluation input và giữ document identity nhất quán qua các index.
- **Bằng chứng:** Baseline Hit Rate 1.0 giảm còn 0.0 khi corrupted và trở lại 1.0 sau repair; Token F1 lần lượt là 1.0, 0.7246 và 1.0.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng:** Ô text rỗng đọc từ CSV có thể thành `NaN` float và gây lỗi khi rebuild `text_for_embedding`.
- **Nguyên nhân gốc:** CSV parser biểu diễn ô rỗng khác với chuỗi rỗng.
- **Cách xử lý:** Chuẩn hóa an toàn text trước khi thao tác chuỗi trong cleaning/corruption flow.
- **Cách xác minh:** Chạy lại `python script/run_corruption_flow.py`; flow tạo được corrupted và repaired artifacts.
- **Bài học:** Các bước xử lý text phải xử lý cả `None`, `NaN` và chuỗi rỗng.

## 7. Hiểu biết về luồng end-to-end

1. Crossref API hoặc snapshot được parse thành `PaperRecord`, cleaning tạo context embedding, rồi embedding và metadata DOI được lưu trong ChromaDB.
2. Evaluation set chứa câu hỏi, ground truth và DOI mục tiêu. Retrieval hit khi một DOI trong kết quả thuộc `ground_truth_doc_ids`; Token F1 đo mức trùng token giữa câu trả lời và ground truth.
3. Quality checks kiểm tra null, uniqueness và summary length. Freshness monitoring tập trung vào `age_days` và tỷ lệ record quá 180 ngày.
4. Dùng cùng test set giúp đo riêng tác động của corruption và repair.
5. Repair thành công khi raw/clean artifacts được rebuild, quality gate PASS và metrics repaired trở về baseline.

## 8. Phân tích kết quả

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét |
|---|---:|---:|---:|---|
| `retrieval_hit_rate` | 1.0 | 0.0 | 1.0 | Hit Rate giảm hoàn toàn rồi phục hồi |
| `mean_token_f1` | 1.0 | 0.7246 | 1.0 | Token F1 giảm 0.2754 khi corrupted |
| `judge_accuracy` | 1.0 | 0.8 | 1.0 | Judge accuracy giảm 0.2 rồi phục hồi |
| `mean_judge_score` | 5.0 | 3.6 | 5.0 | Điểm trung bình giảm 1.4 khi corrupted |
| Quality checks | PASS | FAIL | PASS | Duplicate/summary corruption bị phát hiện |
| Freshness status | FRESH (1/24; 0.0417) | FRESH (3/21; 0.1429) | FRESH (1/24; 0.0417) | Tất cả vẫn dưới ngưỡng 25% |

### Kết luận từ số liệu

Blank summary, duplicate rows và nội dung bị biến đổi ảnh hưởng rõ nhất đến quality gate và context retrieval. Corrupted Quality Gate chuyển sang FAIL, Hit Rate giảm từ 1.0 xuống 0.0 và Token F1 giảm từ 1.0 xuống 0.7246.

Repair rebuild từ raw snapshot, sau đó clean và index lại. Kết quả repaired khôi phục 24 dòng, Quality Gate PASS, Hit Rate về 1.0 và Token F1 về 1.0.

## 9. Bài học và hướng cải thiện

1. Data lineage và document ID phải ổn định từ ingestion đến evaluation.
2. Quality checks cần kiểm tra schema, nội dung và uniqueness; freshness riêng không đủ phát hiện mọi corruption.
3. RAG metrics có thể giảm dù pipeline không crash, nên cần kết hợp quality gate với retrieval evaluation.

Nếu có thêm thời gian, nhóm nên bổ sung automated test suite cho parser, cleaning, corruption và report; đồng thời bật Ragas trong môi trường có cấu hình LLM phù hợp.

## 10. Cam kết của thành viên

- [x] Nội dung phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module phụ trách.
- [x] Các kết luận về kết quả có artifact hoặc metric để đối chiếu.
- [x] Không ghi nhận thành công cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo không sao chép nguyên văn báo cáo nhóm.

**Họ và tên:** Vũ Bá Anh

**Ngày xác nhận:** 2026-09-26
