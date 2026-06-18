from __future__ import annotations

from typing import Any, Dict, List


def expression_from_problem(problem: Dict[str, Any]) -> str:
    return str(problem["expression"])


def plan_from_problem(problem: Dict[str, Any]) -> List[str]:
    plan = problem.get("plan")
    if plan:
        return list(plan)
    return [f"Compute {expression_from_problem(problem)}", "Return the numeric result"]


def candidate_expressions(problem: Dict[str, Any]) -> List[str]:
    correct = expression_from_problem(problem)
    distractors = problem.get("distractors", [])
    return [correct, *distractors]

