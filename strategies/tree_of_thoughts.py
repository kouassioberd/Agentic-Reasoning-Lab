from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from .base import Trace
from .problem_solver import candidate_expressions, expression_from_problem
from tools import Calculator


class TreeOfThoughtsStrategy:
    name = "tree_of_thoughts"

    def __init__(self, beam_width: int = 2, calculator: Optional[Calculator] = None) -> None:
        self.beam_width = beam_width
        self.calculator = calculator or Calculator()

    def solve(self, problem: Dict[str, Any]) -> Trace:
        trace = Trace.create(self.name, problem["id"])
        correct_expression = expression_from_problem(problem)
        branches: List[Dict[str, Any]] = []

        for depth, expression in enumerate(candidate_expressions(problem), start=1):
            start = time.perf_counter()
            score = self._score_expression(expression, correct_expression)
            branch = {"depth": depth, "expression": expression, "score": score}
            branches.append(branch)
            trace.add_event(
                "branch",
                {"candidate": expression, "depth": depth},
                {"score": score},
                start,
            )

        start = time.perf_counter()
        beam = sorted(branches, key=lambda item: item["score"], reverse=True)[: self.beam_width]
        trace.add_event(
            "score",
            {"branches": branches},
            {"beam": beam},
            start,
        )

        start = time.perf_counter()
        selected = beam[0]["expression"]
        answer = self.calculator.run(selected)
        trace.answer = answer
        trace.metadata["tree"] = branches
        trace.add_event(
            "tool_call",
            {"tool": self.calculator.name, "selected_expression": selected},
            {"answer": answer},
            start,
        )
        return trace

    @staticmethod
    def _score_expression(candidate: str, correct: str) -> float:
        candidate_terms = set(candidate.replace("(", " ").replace(")", " ").split())
        correct_terms = set(correct.replace("(", " ").replace(")", " ").split())
        overlap = len(candidate_terms & correct_terms) / max(1, len(correct_terms))
        return 1.0 if candidate == correct else 0.25 + 0.5 * overlap
