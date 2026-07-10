from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

try:
    from intellicode.native._native import MemoryPool, NativeRuntime
except ImportError:
    MemoryPool = None
    NativeRuntime = None


@dataclass(frozen=True)
class NativeExecutionMetrics:
    count: int
    mean_ms: float
    p50_ms: float
    p95_ms: float
    p99_ms: float
    throughput_per_second: float


def native_available() -> bool:
    return NativeRuntime is not None


def parallel_map(values: Iterable[str], function: Callable[[str], str], workers: int = 0) -> tuple[list[str], NativeExecutionMetrics | None]:
    items = list(values)
    if NativeRuntime is None:
        return [function(value) for value in items], None
    result = NativeRuntime(workers).map(items, function)
    metrics = result.metrics
    return result.outputs, NativeExecutionMetrics(
        count=metrics.count,
        mean_ms=metrics.mean_ms,
        p50_ms=metrics.p50_ms,
        p95_ms=metrics.p95_ms,
        p99_ms=metrics.p99_ms,
        throughput_per_second=metrics.throughput_per_second,
    )
