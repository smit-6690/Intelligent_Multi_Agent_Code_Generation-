from __future__ import annotations

from typing import Any

from intellicode.schemas import Problem
from intellicode.utils import parse_json_object

from .base import Agent


class TestDesignerAgent(Agent):
    def design(self, problem: Problem, code: str) -> dict[str, Any]:
        return parse_json_object(self.call(prompt=problem.prompt, code=code))
