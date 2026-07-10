from __future__ import annotations

import os
from pathlib import Path

from intellicode.llm.base import LLMBackend
from intellicode.llm.mock_backend import MockBackend
from intellicode.orchestrator import MultiAgentCodeGenerator
from intellicode.rag import FaissRetriever, NullRetriever


def create_pipeline(
    model_id: str,
    prompt_file: str | Path,
    adapter_path: str | None = None,
    rag_dir: str | None = None,
    mock: bool = False,
    max_repairs: int = 2,
) -> MultiAgentCodeGenerator:
    backend: LLMBackend
    if mock:
        backend = MockBackend()
    else:
        from intellicode.llm.transformers_backend import TransformersBackend

        backend = TransformersBackend(
            model_id=model_id,
            adapter_path=adapter_path,
            load_in_4bit=os.getenv("INTELLICODE_4BIT", "1") == "1",
            temperature=float(os.getenv("INTELLICODE_TEMPERATURE", "0")),
        )
    retriever = FaissRetriever(rag_dir) if rag_dir else NullRetriever()
    return MultiAgentCodeGenerator(
        backend=backend,
        prompt_file=prompt_file,
        retriever=retriever,
        max_repairs=max_repairs,
    )
