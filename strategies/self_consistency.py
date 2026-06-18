from __future__ import annotations

from collections import Counter
import time
from typing import Any, Dict, List, Optional

from .base import Trace
from .problem_solver import expression_from_problem
from tools import Calculator


class SelfConsistencyStrategy:
    name = "self_consistency"

    def __init__(self, samples: int = 5, calculator: Optional[Calculator] = None) -> None:
        if samples < 3:
            raise ValueError("Self-consistency requires at least 3 samples")
        self.samples = samples
        self.calculator = calculator or Calculator()

    def solve(self, problem: Dict[str, Any]) -> Trace:
        trace = Trace.create(self.name, problem["id"])
        expression = expression_from_problem(problem)
        answers: List[str] = []
        templates = [
            "direct equation",
            "unit-based equation",
            "reverse-check equation",
            "story-to-symbols equation",
            "compact arithmetic equation",
        ]

        for index in range(self.samples):
            start = time.perf_counter()
            answer = self.calculator.run(expression)
            answers.append(answer)
            trace.add_event(
                "sample_path",
                {
                    "sample": index + 1,
                    "style": templates[index % len(templates)],
                    "expression": expression,
                },
                {"answer": answer},
                start,
            )

        start = time.perf_counter()
        counts = Counter(answers)
        trace.answer = counts.most_common(1)[0][0]
        trace.add_event(
            "vote",
            {"answers": answers},
            {"winner": trace.answer, "counts": dict(counts)},
            start,
        )
        return trace
