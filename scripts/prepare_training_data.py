from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from datasets import load_dataset


def mbpp_rows(limit: int | None) -> list[dict[str, str]]:
    dataset = load_dataset("google-research-datasets/mbpp", "sanitized", split="train")
    rows = []
    for item in dataset:
        prompt = str(item.get("prompt") or item.get("text") or "").strip()
        code = str(item.get("code") or "").strip()
        if prompt and code:
            rows.append({"instruction": prompt, "response": code, "source": "mbpp"})
        if limit and len(rows) >= limit:
            break
    return rows


def codecontest_rows(limit: int | None) -> list[dict[str, str]]:
    dataset = load_dataset("deepmind/code_contests", split="train", streaming=True)
    rows = []
    for item in dataset:
        description = str(item.get("description") or "").strip()
        solutions = item.get("solutions") or {}
        languages = solutions.get("language", [])
        code_values = solutions.get("solution", [])
        selected = None
        for language, code in zip(languages, code_values):
            if str(language).lower() in {"python", "python3", "3"}:
                selected = str(code).strip()
                break
        if description and selected:
            rows.append({
                "instruction": description,
                "response": selected,
                "source": "code_contests",
            })
        if limit and len(rows) >= limit:
            break
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/training/code_training.jsonl")
    parser.add_argument("--mbpp-limit", type=int)
    parser.add_argument("--codecontests-limit", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    rows = mbpp_rows(args.mbpp_limit) + codecontest_rows(args.codecontests_limit)
    random.Random(args.seed).shuffle(rows)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")
    print(f"rows={len(rows)}")
    print(f"output={output}")


if __name__ == "__main__":
    main()
