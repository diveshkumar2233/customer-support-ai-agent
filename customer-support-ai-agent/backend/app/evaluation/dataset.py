"""Loader for the evaluation test dataset (data/evaluation/test_questions.json)."""
import json
from pathlib import Path


def load_eval_dataset(path: str = "data/evaluation/test_questions.json") -> list[dict]:
    with open(Path(path), "r", encoding="utf-8") as f:
        return json.load(f)
