"""Convert the public e-commerce support Parquet dataset into RAG-ready Markdown."""
import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT_ROOT / "data" / "external" / "ecommerce_customer_support_qa.parquet"
OUTPUT = PROJECT_ROOT / "data" / "documents" / "ecommerce_customer_support_qa.md"


def main() -> None:
    data = pd.read_parquet(SOURCE)
    entries: list[str] = ["# E-commerce Customer Support Knowledge Base\n"]

    for number, row in data.iterrows():
        try:
            knowledge = json.loads(row["qa"]).get("knowledge", [])
        except (TypeError, json.JSONDecodeError):
            knowledge = []

        entries.append(
            f"## Support Case {number + 1}: {row['issue_category']}\n"
            f"Category: {row['issue_area']} > {row['issue_sub_category']}\n"
        )
        for item in knowledge:
            question = item.get("customer_summary_question", "").strip()
            solution = item.get("agent_summary_solution", "").strip()
            if question and solution:
                entries.append(f"Customer question: {question}\nSupport answer: {solution}\n")

    OUTPUT.write_text("\n".join(entries), encoding="utf-8")
    print(f"Created {OUTPUT} from {len(data)} support records.")


if __name__ == "__main__":
    main()
