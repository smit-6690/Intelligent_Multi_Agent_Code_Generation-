from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def validate_samples(path: Path) -> int:
    count = 0
    seen: set[str] = set()
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            row = json.loads(line)
            if set(row) < {"task_id", "completion"}:
                raise ValueError(f"Missing fields on line {line_number}")
            if row["task_id"] in seen:
                raise ValueError(f"Duplicate task_id: {row['task_id']}")
            seen.add(row["task_id"])
            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", default="artifacts/humaneval_samples.jsonl")
    parser.add_argument("--dataset", choices=["humaneval", "humaneval+"], default="humaneval")
    parser.add_argument("--parallel", type=int, default=4)
    args = parser.parse_args()
    samples = Path(args.samples)
    count = validate_samples(samples)
    print(f"validated_samples={count}")
    command = [
        sys.executable,
        "-m",
        "evalplus.evaluate",
        "--dataset",
        args.dataset,
        "--samples",
        str(samples),
        "--parallel",
        str(args.parallel),
    ]
    raise SystemExit(subprocess.run(command, check=False).returncode)


if __name__ == "__main__":
    main()
