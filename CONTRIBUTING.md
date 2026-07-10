# Contributing

1. Create a feature branch.
2. Install development dependencies with `pip install -e ".[dev]"`.
3. Run `ruff check .`, `mypy src/intellicode`, and `pytest`.
4. Include tests for behavioral changes.
5. Do not commit model weights, datasets without a compatible license, secrets, or generated benchmark claims without raw evidence.
