from __future__ import annotations

from abc import ABC, abstractmethod


class LLMBackend(ABC):
    @abstractmethod
    def generate(self, system: str, user: str, max_new_tokens: int = 1024) -> str:
        raise NotImplementedError
