from __future__ import annotations

from intellicode.schemas import Review, Specification, TestReport
from intellicode.utils import parse_json_object

from .base import Agent


class JudgeAgent(Agent):
    def decide(self, specification: Specification, review: Review, report: TestReport) -> bool:
        data = parse_json_object(self.call(
            specification=specification.model_dump(),
            review=review.model_dump(),
            test_report=report.model_dump(),
        ))
        return bool(data.get("accept", False)) and report.passed and review.approved
