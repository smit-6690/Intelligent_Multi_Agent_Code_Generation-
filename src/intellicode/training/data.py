from __future__ import annotations


def format_record(record: dict[str, object]) -> str:
    instruction = str(record.get("instruction") or record.get("prompt") or "").strip()
    response = str(record.get("response") or record.get("completion") or "").strip()
    if not instruction or not response:
        raise ValueError("Each record requires instruction/prompt and response/completion")
    return f"### Instruction\n{instruction}\n\n### Response\n{response}"
