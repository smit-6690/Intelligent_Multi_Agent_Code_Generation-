from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Problem(BaseModel):
    task_id: str
    prompt: str
    entry_point: str | None = None
    canonical_solution: str | None = None
    test: str | None = None
    language: Literal["python", "cpp"] = "python"


class Specification(BaseModel):
    task_id: str
    language: str
    function_signature: str
    objective: str
    inputs: list[str]
    outputs: str
    constraints: list[str]
    edge_cases: list[str]
    algorithm_hints: list[str]
    original_prompt: str


class Candidate(BaseModel):
    code: str
    explanation: str = ""
    complexity: str = ""


class Review(BaseModel):
    approved: bool
    score: int = Field(ge=0, le=10)
    defects: list[str]
    recommendations: list[str]


class TestReport(BaseModel):
    passed: bool
    stage: str
    stdout: str = ""
    stderr: str = ""
    return_code: int | None = None
    duration_seconds: float = 0.0


class AgentTrace(BaseModel):
    agent: str
    input_summary: str
    output: dict[str, Any]


class GenerationResult(BaseModel):
    task_id: str
    completion: str
    passed: bool
    attempts: int
    review: Review
    test_report: TestReport
    traces: list[AgentTrace]
