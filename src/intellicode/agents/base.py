from __future__ import annotations

from intellicode.llm.base import LLMBackend
from intellicode.prompts import PromptRegistry


class Agent:
    def __init__(self, backend: LLMBackend, prompts: PromptRegistry, prompt_name: str):
        self.backend = backend
        self.template = prompts.get(prompt_name)

    def call(self, **values: object) -> str:
        system, user = self.template.render(**values)
        return self.backend.generate(system, user)
