from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import requests

from intellicode.evaluation import validate_humaneval

URL = "https://raw.githubusercontent.com/openai/human-eval/master/data/HumanEval.jsonl.gz"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/humaneval/HumanEval.jsonl.gz")
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(URL, timeout=60)
    response.raise_for_status()
    output.write_bytes(response.content)
    count = validate_humaneval(output)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print(f"downloaded={output}")
    print(f"tasks={count}")
    print(f"sha256={digest}")


if __name__ == "__main__":
    main()
