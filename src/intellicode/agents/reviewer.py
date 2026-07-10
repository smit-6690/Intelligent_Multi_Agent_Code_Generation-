from __future__ import annotations

from intellicode.schemas import Review, Specification, TestReport
from intellicode.utils import parse_json_object

from .base import Agent


class ReviewerAgent(Agent):
    def review(
        self,
        specification: Specification,
        code: str,
        test_notes: dict[str, object],
        test_report: TestReport,
    ) -> Review:
        data = parse_json_object(self.call(
            specification=specification.model_dump(),
            code=code,
            test_notes=test_notes,
            test_report=test_report.model_dump(),
        ))
        return Review(
            approved=bool(data.get("approved", False)),
            score=int(data.get("score", 0)),
            defects=[str(x) for x in data.get("defects", [])],
            recommendations=[str(x) for x in data.get("recommendations", [])],
        )
