from __future__ import annotations

import subprocess
import sys
import tempfile
import time
from pathlib import Path

from intellicode.schemas import Problem, TestReport
from intellicode.utils import humaneval_completion


class LocalSandbox:
    def __init__(self, timeout_seconds: int = 8):
        self.timeout_seconds = timeout_seconds

    def evaluate(self, problem: Problem, code: str) -> TestReport:
        if problem.language != "python":
            return TestReport(passed=False, stage="unsupported", stderr="Only Python is supported")
        if not problem.test or not problem.entry_point:
            return self._syntax_check(code)
        completion = humaneval_completion(problem.prompt, code, problem.entry_point)
        program = problem.prompt + completion + "\n\n" + problem.test + f"\n\ncheck({problem.entry_point})\n"
        return self._run_python(program, "humaneval")

    def _syntax_check(self, code: str) -> TestReport:
        started = time.perf_counter()
        try:
            compile(code, "candidate.py", "exec")
            return TestReport(
                passed=True,
                stage="syntax",
                duration_seconds=time.perf_counter() - started,
            )
        except SyntaxError as error:
            return TestReport(
                passed=False,
                stage="syntax",
                stderr=str(error),
                duration_seconds=time.perf_counter() - started,
            )

    def _run_python(self, program: str, stage: str) -> TestReport:
        started = time.perf_counter()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candidate.py"
            path.write_text(program, encoding="utf-8")
            try:
                completed = subprocess.run(
                    [sys.executable, "-I", str(path)],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                    cwd=directory,
                    check=False,
                )
                return TestReport(
                    passed=completed.returncode == 0,
                    stage=stage,
                    stdout=completed.stdout[-4000:],
                    stderr=completed.stderr[-4000:],
                    return_code=completed.returncode,
                    duration_seconds=time.perf_counter() - started,
                )
            except subprocess.TimeoutExpired as error:
                return TestReport(
                    passed=False,
                    stage=stage,
                    stdout=(error.stdout or "")[-4000:],
                    stderr="Execution timed out",
                    duration_seconds=time.perf_counter() - started,
                )
