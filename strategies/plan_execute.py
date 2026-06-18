from __future__ import annotations

import time
from typing import Any, Dict, Optional

from .base import Trace
from .problem_solver import expression_from_problem, plan_from_problem
from tools import Calculator


class PlanAndExecuteStrategy:
    name = "plan_execute"

    def __init__(self, calculator: Optional[Calculator] = None) -> None:
        self.calculator = calculator or Calculator()

    def solve(self, problem: Dict[str, Any]) -> Trace:
        trace = Trace.create(self.name, problem["id"])
        plan = plan_from_problem(problem)
        start = time.perf_counter()
        trace.add_event(
            "plan",
            {"problem": problem["question"]},
            {"steps": plan},
            start,
        )

        expression = expression_from_problem(problem)
        interim = None
        for index, step in enumerate(plan, start=1):
            start = time.perf_counter()
            if index == len(plan):
                interim = self.calculator.run(expression)
                output = {"result": interim}
                step_type = "tool_call"
            else:
                output = {"status": "ready", "notes": step}
                step_type = "execute_step"
            trace.add_event(
                step_type,
                {"step_number": index, "step": step, "expression": expression},
                output,
                start,
            )

        trace.answer = str(interim)
        return trace
