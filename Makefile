.PHONY: install test lint native-build native-test native-benchmark humaneval-data humaneval-generate humaneval-evaluate

install:
	python -m pip install -e ".[dev]"

test:
	pytest -q

lint:
	ruff check src scripts tests
	mypy src

native-build:
	cmake -S cpp -B build/native -DCMAKE_BUILD_TYPE=Release
	cmake --build build/native --parallel

native-test: native-build
	ctest --test-dir build/native --output-on-failure

native-benchmark: native-build
	./build/native/intellicode_runtime_benchmark 10000

humaneval-data:
	python scripts/download_humaneval.py

humaneval-generate:
	python scripts/generate_humaneval.py --dataset data/humaneval/HumanEval.jsonl.gz --output artifacts/humaneval_samples.jsonl --trace-output artifacts/humaneval_traces.jsonl

humaneval-evaluate:
	python scripts/evaluate_humaneval.py --samples artifacts/humaneval_samples.jsonl --dataset humaneval
