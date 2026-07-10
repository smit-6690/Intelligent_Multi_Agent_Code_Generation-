from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from intellicode.native import native_available, parallel_map


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks", type=int, default=10000)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--output", type=Path, default=Path("artifacts/benchmarks/native_runtime.json"))
    args = parser.parse_args()
    inputs = ["generate-code"] * args.tasks
    started = time.perf_counter()
    outputs, metrics = parallel_map(inputs, lambda value: value + "-token" * 20, args.workers)
    wall_seconds = time.perf_counter() - started
    payload = {
        "native_extension_available": native_available(),
        "tasks": len(outputs),
        "wall_seconds": wall_seconds,
        "end_to_end_throughput_per_second": len(outputs) / wall_seconds if wall_seconds else 0.0,
        "native_metrics": metrics.__dict__ if metrics else None,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
