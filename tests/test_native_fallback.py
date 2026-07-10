from intellicode.native import parallel_map


def test_parallel_map_returns_outputs() -> None:
    outputs, metrics = parallel_map(["a", "b"], str.upper)
    assert outputs == ["A", "B"]
    if metrics is not None:
        assert metrics.count == 2
