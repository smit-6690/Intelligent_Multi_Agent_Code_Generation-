from __future__ import annotations

import argparse
import json
from pathlib import Path

from intellicode.factory import create_pipeline
from intellicode.schemas import Problem


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt")
    parser.add_argument("--task-id", default="interactive/0")
    parser.add_argument("--entry-point")
    parser.add_argument("--model-id", default="Qwen/Qwen2.5-Coder-1.5B-Instruct")
    parser.add_argument("--adapter-path")
    parser.add_argument("--rag-dir")
    parser.add_argument("--prompt-file", default="configs/agent_prompts.yaml")
    parser.add_argument("--mock", action="store_true")
    args = parser.parse_args()
    pipeline = create_pipeline(
        model_id=args.model_id,
        prompt_file=args.prompt_file,
        adapter_path=args.adapter_path,
        rag_dir=args.rag_dir,
        mock=args.mock,
    )
    result = pipeline.solve(Problem(
        task_id=args.task_id,
        prompt=args.prompt,
        entry_point=args.entry_point,
    ))
    print(json.dumps(result.model_dump(), indent=2))


if __name__ == "__main__":
    main()
