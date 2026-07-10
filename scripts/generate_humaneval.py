from __future__ import annotations

import argparse
import json
from pathlib import Path

from tqdm import tqdm

from intellicode.evaluation import read_humaneval, validate_humaneval
from intellicode.factory import create_pipeline
from intellicode.utils import humaneval_completion


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="data/humaneval/HumanEval.jsonl.gz")
    parser.add_argument("--output", default="artifacts/humaneval_samples.jsonl")
    parser.add_argument("--trace-output", default="artifacts/humaneval_traces.jsonl")
    parser.add_argument("--model-id", default="Qwen/Qwen2.5-Coder-1.5B-Instruct")
    parser.add_argument("--adapter-path")
    parser.add_argument("--rag-dir")
    parser.add_argument("--prompt-file", default="configs/agent_prompts.yaml")
    parser.add_argument("--max-repairs", type=int, default=2)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--mock", action="store_true")
    args = parser.parse_args()

    validate_humaneval(args.dataset)
    pipeline = create_pipeline(
        model_id=args.model_id,
        prompt_file=args.prompt_file,
        adapter_path=args.adapter_path,
        rag_dir=args.rag_dir,
        mock=args.mock,
        max_repairs=args.max_repairs,
    )
    tasks = list(read_humaneval(args.dataset))
    if args.limit is not None:
        tasks = tasks[: args.limit]

    output = Path(args.output)
    traces = Path(args.trace_output)
    output.parent.mkdir(parents=True, exist_ok=True)
    traces.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as samples_handle, traces.open(
        "w", encoding="utf-8"
    ) as trace_handle:
        for task in tqdm(tasks, desc="HumanEval"):
            result = pipeline.solve(task)
            samples_handle.write(json.dumps({
                "task_id": task.task_id,
                "completion": humaneval_completion(
                    task.prompt, result.completion, task.entry_point
                ),
            }) + "\n")
            trace_handle.write(json.dumps(result.model_dump()) + "\n")
            samples_handle.flush()
            trace_handle.flush()


if __name__ == "__main__":
    main()
