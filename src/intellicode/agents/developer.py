from __future__ import annotations

from intellicode.schemas import Candidate, Specification
from intellicode.utils import extract_code

from .base import Agent


class DeveloperAgent(Agent):
    def generate(self, specification: Specification, rag_context: str = "") -> Candidate:
        raw = self.call(
            language=specification.language,
            specification=specification.model_dump(),
            rag_context=rag_context or "No relevant context retrieved.",
        )
        return Candidate(code=extract_code(raw))
