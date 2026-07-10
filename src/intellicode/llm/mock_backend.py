from __future__ import annotations

import json

from .base import LLMBackend


class MockBackend(LLMBackend):
    def generate(self, system: str, user: str, max_new_tokens: int = 1024) -> str:
        if "Specification Analyst" in system:
            return json.dumps({
                "function_signature": "def solve(*args):",
                "objective": "Implement the requested behavior.",
                "inputs": ["Inputs described by the task"],
                "outputs": "Output described by the task",
                "constraints": [],
                "edge_cases": [],
                "algorithm_hints": [],
            })
        if "Test Designer" in system:
            return json.dumps({"risk_areas": [], "edge_cases": [], "adversarial_cases": []})
        if "Senior Code Reviewer" in system:
            return json.dumps({"approved": True, "score": 8, "defects": [], "recommendations": []})
        if "Final Judge" in system:
            return json.dumps({"accept": True, "reason": "Mock acceptance"})
        return "def solve(*args):\n    return None"
