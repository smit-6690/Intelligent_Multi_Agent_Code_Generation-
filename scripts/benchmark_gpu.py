import argparse
import json
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Profile PyTorch inference optimizations")
    parser.add_argument("--model-id", default="Qwen/Qwen2.5-Coder-1.5B-Instruct")
    parser.add_argument("--prompt", default="Write a Python binary search function.")
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--max-new-tokens", type=int, default=64)
    parser.add_argument("--output", default="artifacts/gpu_benchmark.json")
    parser.add_argument("--compile", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU is required for this benchmark")

    tokenizer = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id,
        torch_dtype=torch.bfloat16,
        device_map="cuda",
        attn_implementation="sdpa",
    ).eval()
    if args.compile:
        model = torch.compile(model, mode="reduce-overhead")

    inputs = tokenizer(args.prompt, return_tensors="pt").to("cuda")
    with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
        model.generate(**inputs, max_new_tokens=8)
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()

    latencies = []
    with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
        for _ in range(args.iterations):
            started = time.perf_counter()
            output = model.generate(**inputs, max_new_tokens=args.max_new_tokens)
            torch.cuda.synchronize()
            latencies.append(time.perf_counter() - started)

    generated = output.shape[-1] - inputs["input_ids"].shape[-1]
    result = {
        "model_id": args.model_id,
        "gpu": torch.cuda.get_device_name(0),
        "torch_compile": args.compile,
        "dtype": "bfloat16",
        "attention": "sdpa",
        "iterations": args.iterations,
        "mean_latency_seconds": sum(latencies) / len(latencies),
        "generated_tokens_last_iteration": int(generated),
        "tokens_per_second_last_iteration": generated / latencies[-1],
        "peak_memory_gb": torch.cuda.max_memory_allocated() / (1024**3),
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
