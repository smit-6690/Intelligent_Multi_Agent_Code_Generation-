from __future__ import annotations

from intellicode.schemas import Candidate, Review, Specification, TestReport
from intellicode.utils import extract_code

from .base import Agent


class RepairAgent(Agent):
    def repair(
        self,
        specification: Specification,
        candidate: Candidate,
        review: Review,
        test_report: TestReport,
    ) -> Candidate:
        raw = self.call(
            specification=specification.model_dump(),
            code=candidate.code,
            review=review.model_dump(),
            test_report=test_report.model_dump(),
        )
        return Candidate(code=extract_code(raw))
