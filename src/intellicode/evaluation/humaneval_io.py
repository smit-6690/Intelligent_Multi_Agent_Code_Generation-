from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Iterator

from intellicode.schemas import Problem


def read_humaneval(path: str | Path) -> Iterator[Problem]:
    source = Path(path)
    opener = gzip.open if source.suffix == ".gz" else open
    with opener(source, "rt", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            yield Problem(
                task_id=row["task_id"],
                prompt=row["prompt"],
                entry_point=row["entry_point"],
                canonical_solution=row.get("canonical_solution"),
                test=row.get("test"),
                language="python",
            )


def validate_humaneval(path: str | Path) -> int:
    tasks = list(read_humaneval(path))
    identifiers = {task.task_id for task in tasks}
    if len(tasks) != 164:
        raise ValueError(f"Expected 164 HumanEval tasks, found {len(tasks)}")
    if len(identifiers) != len(tasks):
        raise ValueError("HumanEval contains duplicate task IDs")
    return len(tasks)
