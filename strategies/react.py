from __future__ import annotations

import time
from typing import Any, Dict, Optional

from .base import Trace
from .problem_solver import expression_from_problem
from tools import Calculator


class ReActStrategy:
    name = "react"

    def __init__(self, calculator: Optional[Calculator] = None) -> None:
        self.calculator = calculator or Calculator()

    def solve(self, problem: Dict[str, Any]) -> Trace:
        trace = Trace.create(self.name, problem["id"])
        start = time.perf_counter()
        expression = expression_from_problem(problem)
        trace.add_event(
            "reason",
            {"problem": problem["question"]},
            {"thought": f"I should translate the story into {expression} and calculate it."},
            start,
        )

        start = time.perf_counter()
        observation = self.calculator.run(expression)
        trace.add_event(
            "tool_call",
            {"tool": self.calculator.name, "expression": expression},
            {"observation": observation},
            start,
        )

        start = time.perf_counter()
        trace.answer = observation
        trace.add_event(
            "reason",
            {"observation": observation},
            {"final_answer": trace.answer},
            start,
        )
        return trace
