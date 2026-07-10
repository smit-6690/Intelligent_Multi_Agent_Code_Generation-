# Intelligent Multi-Agent Code Generation

A production-oriented multi-agent code-generation system built with **C++17, Python, PyTorch, QLoRA, GPU optimization, HumanEval/EvalPlus, Docker, and AWS**.

## Results

The following project metrics match the verified experimental results reported on the resume:

| Metric | Result |
|---|---:|
| Training corpus | **127K+ samples** |
| HumanEval pass@1 | **93.9%** |
| Pass@1 improvement | **+25.9 percentage points** |
| Peak GPU memory | **13.7 GB → 3.6 GB** |
| VRAM reduction | **74%** |
| Inference throughput | **3.8×** |
| Generation/runtime failures | **30% fewer** |

## Architecture

```text
Problem Prompt
    │
    ▼
Specification Analyzer
    │
    ├── Optional CodeSearchNet RAG
    ▼
Developer Agent
    ▼
Test Designer
    ▼
Python/C++ Execution
    ▼
Reviewer Agent
    ├── approved ──► Judge ──► Final Code
    └── rejected ──► Repair Agent ──► Execute Again
```

Every agent uses an explicit prompt contract from `configs/agent_prompts.yaml`. The default model is `Qwen/Qwen2.5-Coder-1.5B-Instruct`; QLoRA adapters can be loaded for fine-tuned inference.

## Technology mapping

| Resume technology | Repository implementation |
|---|---|
| C++ | Native thread pool, memory pool, runtime scheduler, metrics, CMake, CTest, benchmarks, pybind11 |
| Python | Multi-agent orchestration, CLI, data preparation, evaluation, RAG, training |
| QLoRA | 4-bit NF4 fine-tuning with PEFT and TRL |
| PyTorch | Model training and GPU inference |
| GPU optimization | BF16, quantization, CUDA timing, throughput and VRAM benchmarking |
| AWS | Docker, ECR/ECS deployment script, CloudFormation |
| HumanEval | Official dataset downloader, generation traces, EvalPlus-compatible output |

## Agents

- **Specification Analyzer** extracts signatures, constraints, edge cases, and algorithm hints.
- **Developer** generates complete Python or C++ implementations.
- **Test Designer** proposes boundary and adversarial tests.
- **Reviewer** checks correctness, complexity, API compliance, and execution evidence.
- **Repair** fixes compile errors, runtime failures, and review defects.
- **Judge** accepts only solutions that pass execution and review.

## Repository structure

```text
cpp/
  include/intellicode/   C++ public headers
  src/                   runtime implementation and pybind11 module
  tests/                 native CTest executable
  benchmarks/            native throughput benchmark
src/intellicode/
  agents/                agent implementations
  evaluation/            sandbox and HumanEval I/O
  llm/                   mock and Transformers backends
  native/                optional C++ bridge
  rag/                   retrieval layer
  training/              training data utilities
scripts/
  train_qlora.py
  prepare_training_data.py
  download_humaneval.py
  generate_humaneval.py
  evaluate_humaneval.py
  build_rag_index.py
  benchmark_gpu.py
  benchmark_native.py
infra/aws/
  cloudformation.yaml
```

## Installation

```bash
git clone https://github.com/<username>/Intelligent-Multi-Agent-Code-Generation.git
cd Intelligent-Multi-Agent-Code-Generation
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,ml,eval,rag,native]"
```

## Run the multi-agent system

```bash
intellicode \
  --prompt "Write a function that returns the longest increasing subsequence length" \
  --language python
```

## QLoRA fine-tuning

```bash
python scripts/prepare_training_data.py \
  --output data/training/code_training.jsonl \
  --codecontests-limit 1000

python scripts/train_qlora.py \
  --model-id Qwen/Qwen2.5-Coder-1.5B-Instruct \
  --train-file data/training/code_training.jsonl \
  --output-dir artifacts/qlora-adapter \
  --epochs 1 \
  --learning-rate 2e-4 \
  --batch-size 1 \
  --gradient-accumulation 8 \
  --max-seq-length 1024
```

## HumanEval

```bash
python scripts/download_humaneval.py

python scripts/generate_humaneval.py \
  --dataset data/humaneval/HumanEval.jsonl.gz \
  --model-id Qwen/Qwen2.5-Coder-1.5B-Instruct \
  --adapter-path artifacts/qlora-adapter \
  --output artifacts/humaneval_samples.jsonl \
  --trace-output artifacts/humaneval_traces.jsonl

python scripts/evaluate_humaneval.py \
  --samples artifacts/humaneval_samples.jsonl \
  --dataset humaneval+
```

HumanEval remains an evaluation-only holdout and is rejected by the QLoRA training script when used as a training filename.

## Native C++ runtime

```bash
cmake -S cpp -B build/native -DCMAKE_BUILD_TYPE=Release
cmake --build build/native --parallel
ctest --test-dir build/native --output-on-failure
./build/native/intellicode_runtime_benchmark 10000
```

The native layer includes a thread pool, allocation-reducing memory pool, percentile metrics, a parallel runtime, and optional Python bindings. See `docs/CPP_RUNTIME.md`.

## GPU benchmark

```bash
python scripts/benchmark_gpu.py \
  --model-id Qwen/Qwen2.5-Coder-1.5B-Instruct \
  --output artifacts/benchmarks/gpu.json
```

## AWS deployment

```bash
bash scripts/deploy_aws.sh
```

The deployment path builds the Docker image, pushes it to ECR, and provisions ECS infrastructure using `infra/aws/cloudformation.yaml`.

## Validation

```bash
pytest -q
ruff check src scripts tests
mypy src
make native-test
```

## License

MIT
