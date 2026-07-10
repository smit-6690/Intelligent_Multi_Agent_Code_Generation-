import gzip
import json

from intellicode.evaluation.humaneval_io import read_humaneval


def test_read_humaneval(tmp_path) -> None:
    path = tmp_path / "HumanEval.jsonl.gz"
    row = {
        "task_id": "HumanEval/0",
        "prompt": "def add(a, b):\n    pass",
        "entry_point": "add",
        "canonical_solution": "    return a + b",
        "test": "def check(candidate):\n    assert candidate(1, 2) == 3",
    }
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        handle.write(json.dumps(row) + "\n")
    tasks = list(read_humaneval(path))
    assert tasks[0].task_id == "HumanEval/0"
    assert tasks[0].entry_point == "add"
