from intellicode.evaluation.sandbox import LocalSandbox
from intellicode.schemas import Problem


def test_humaneval_candidate_execution() -> None:
    problem = Problem(
        task_id="HumanEval/0",
        prompt="def add(a, b):\n    \"\"\"Add values.\"\"\"",
        entry_point="add",
        test="def check(candidate):\n    assert candidate(1, 2) == 3",
    )
    report = LocalSandbox().evaluate(problem, "def add(a, b):\n    return a + b")
    assert report.passed
