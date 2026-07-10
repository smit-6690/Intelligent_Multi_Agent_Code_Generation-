from __future__ import annotations

from intellicode.schemas import Problem, Specification
from intellicode.utils import parse_json_object, python_signature

from .base import Agent


class SpecAnalyzerAgent(Agent):
    def analyze(self, problem: Problem) -> Specification:
        raw = self.call(task_id=problem.task_id, language=problem.language, prompt=problem.prompt)
        data = parse_json_object(raw)
        signature = data.get("function_signature") or python_signature(
            problem.prompt, problem.entry_point
        )
        return Specification(
            task_id=problem.task_id,
            language=problem.language,
            function_signature=signature,
            objective=str(data.get("objective", "Implement the requested behavior.")),
            inputs=[str(x) for x in data.get("inputs", [])],
            outputs=str(data.get("outputs", "")),
            constraints=[str(x) for x in data.get("constraints", [])],
            edge_cases=[str(x) for x in data.get("edge_cases", [])],
            algorithm_hints=[str(x) for x in data.get("algorithm_hints", [])],
            original_prompt=problem.prompt,
        )
