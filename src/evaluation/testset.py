from __future__ import annotations

from typing import Any

import pandas as pd

from core.utils import first_sentence, write_json


def build_test_set(df: pd.DataFrame, output_path) -> list[dict[str, Any]]:
    """TODO(student): tao bo evaluation set tu cleaned dataframe.

    Pseudo-code:
    1. Kiem tra so luong document toi thieu.
    2. Chon mot so paper dai dien.
    3. Tao nhieu loai cau hoi:
       - summary
       - authors
       - date
       - categories
    4. Moi row can co:
       - id
       - question_type
       - question
       - ground_truth
       - ground_truth_doc_ids
    5. Ghi file JSON vao output_path.
    """
    def text(row: dict[str, Any], key: str) -> str:
        value = row.get(key, "")
        return "" if value is None or pd.isna(value) else str(value).strip()

    candidates = {"summary": [], "authors": [], "date": [], "categories": []}
    for row in df.to_dict(orient="records"):
        title = text(row, "title")
        paper_id = text(row, "paper_id")
        if not title or not paper_id:
            continue
        values = {
            "summary": first_sentence(text(row, "summary")),
            "authors": text(row, "authors_joined"),
            "date": text(row, "published"),
            "categories": text(row, "categories_joined"),
        }
        for question_type, ground_truth in values.items():
            if ground_truth:
                candidates[question_type].append((row, ground_truth))

    counts = {"summary": 3, "authors": 3, "date": 2, "categories": 2}
    questions: list[dict[str, Any]] = []
    for question_type, count in counts.items():
        for row, ground_truth in candidates[question_type][:count]:
            title = text(row, "title")
            paper_id = text(row, "paper_id")
            prompts = {
                "summary": f"What is the summary of '{title}'?",
                "authors": f"Who authored '{title}'?",
                "date": f"When was '{title}' published?",
                "categories": f"What categories does '{title}' belong to?",
            }
            questions.append(
                {
                    "id": f"eval_{len(questions) + 1:03d}",
                    "question_type": question_type,
                    "question": prompts[question_type],
                    "ground_truth": ground_truth,
                    "ground_truth_doc_ids": [paper_id],
                }
            )

    if len(questions) != 10:
        raise ValueError("Not enough non-empty records to build the 10-question test set")
    write_json(output_path, questions)
    return questions
