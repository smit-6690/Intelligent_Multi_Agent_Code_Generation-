# Native C++ Runtime

The C++17 subsystem provides reusable concurrency and performance primitives for latency-sensitive code-generation workloads.

## Components

- `ThreadPool`: bounded worker lifecycle, futures, idle synchronization, and safe shutdown.
- `MemoryPool`: reusable fixed-size blocks to reduce repeated small allocations.
- `MetricsCollector`: mean, p50, p95, p99, and throughput aggregation.
- `NativeRuntime`: parallel string-task execution used by the optional Python extension.
- `pybind11` module: exposes the runtime and memory pool to Python.

## Build

```bash
cmake -S cpp -B build/native -DCMAKE_BUILD_TYPE=Release
cmake --build build/native --parallel
ctest --test-dir build/native --output-on-failure
```

## Python extension

```bash
python -m pip install pybind11
cmake -S cpp -B build/native-python \
  -DINTELLICODE_BUILD_PYTHON=ON \
  -Dpybind11_DIR="$(python -m pybind11 --cmakedir)"
cmake --build build/native-python --parallel
```
