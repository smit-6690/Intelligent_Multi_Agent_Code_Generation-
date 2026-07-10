from __future__ import annotations

import ast
import json
import re
from typing import Any


def extract_code(text: str) -> str:
    fenced = re.search(r"```(?:python|cpp|c\+\+)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    return (fenced.group(1) if fenced else text).strip()


def parse_json_object(text: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("Model did not return a JSON object") from None
        value = json.loads(match.group(0))
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object")
    return value


def python_signature(prompt: str, entry_point: str | None) -> str:
    try:
        tree = ast.parse(prompt)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return ast.unparse(node).split(":", 1)[0] + ":"
    except SyntaxError:
        pass
    return f"def {entry_point or 'solve'}(*args):"


def humaneval_completion(prompt: str, code: str, entry_point: str | None) -> str:
    candidate = extract_code(code)
    if candidate.startswith(prompt):
        return candidate[len(prompt):]
    try:
        tree = ast.parse(candidate)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
                entry_point is None or node.name == entry_point
            ):
                lines = candidate.splitlines()
                if not node.body:
                    return "\n    pass"
                start = node.body[0].lineno - 1
                end = node.end_lineno or len(lines)
                body = lines[start:end]
                minimum = min(
                    len(line) - len(line.lstrip()) for line in body if line.strip()
                )
                normalized = ["    " + line[minimum:] if line.strip() else "" for line in body]
                return "\n" + "\n".join(normalized)
    except SyntaxError:
        pass
    return candidate if candidate.startswith("\n") else "\n" + candidate
