from __future__ import annotations

from pathlib import Path

from intellicode.agents import (
    DeveloperAgent,
    JudgeAgent,
    RepairAgent,
    ReviewerAgent,
    SpecAnalyzerAgent,
    TestDesignerAgent,
)
from intellicode.evaluation.sandbox import LocalSandbox
from intellicode.llm.base import LLMBackend
from intellicode.prompts import PromptRegistry
from intellicode.rag import NullRetriever
from intellicode.schemas import AgentTrace, GenerationResult, Problem, Review


class MultiAgentCodeGenerator:
    def __init__(
        self,
        backend: LLMBackend,
        prompt_file: str | Path,
        retriever: object | None = None,
        max_repairs: int = 2,
        timeout_seconds: int = 8,
    ):
        prompts = PromptRegistry(prompt_file)
        self.spec_agent = SpecAnalyzerAgent(backend, prompts, "spec_analyzer")
        self.developer_agent = DeveloperAgent(backend, prompts, "developer")
        self.test_agent = TestDesignerAgent(backend, prompts, "test_designer")
        self.reviewer_agent = ReviewerAgent(backend, prompts, "reviewer")
        self.repair_agent = RepairAgent(backend, prompts, "repair")
        self.judge_agent = JudgeAgent(backend, prompts, "judge")
        self.retriever = retriever or NullRetriever()
        self.sandbox = LocalSandbox(timeout_seconds)
        self.max_repairs = max_repairs

    def solve(self, problem: Problem) -> GenerationResult:
        traces: list[AgentTrace] = []
        specification = self.spec_agent.analyze(problem)
        traces.append(AgentTrace(
            agent="spec_analyzer",
            input_summary=problem.task_id,
            output=specification.model_dump(),
        ))
        context = self.retriever.retrieve(problem.prompt)
        candidate = self.developer_agent.generate(specification, context)
        traces.append(AgentTrace(
            agent="developer",
            input_summary=specification.objective,
            output={"code": candidate.code},
        ))
        test_notes = self.test_agent.design(problem, candidate.code)
        report = self.sandbox.evaluate(problem, candidate.code)
        review = self.reviewer_agent.review(specification, candidate.code, test_notes, report)
        attempts = 1
        accepted = self.judge_agent.decide(specification, review, report)
        while not accepted and attempts <= self.max_repairs:
            candidate = self.repair_agent.repair(specification, candidate, review, report)
            attempts += 1
            report = self.sandbox.evaluate(problem, candidate.code)
            test_notes = self.test_agent.design(problem, candidate.code)
            review = self.reviewer_agent.review(specification, candidate.code, test_notes, report)
            traces.append(AgentTrace(
                agent="repair",
                input_summary=f"attempt {attempts}",
                output={"code": candidate.code, "passed": report.passed},
            ))
            accepted = self.judge_agent.decide(specification, review, report)
        if not isinstance(review, Review):
            raise TypeError("Reviewer returned an invalid result")
        return GenerationResult(
            task_id=problem.task_id,
            completion=candidate.code,
            passed=accepted,
            attempts=attempts,
            review=review,
            test_report=report,
            traces=traces,
        )
