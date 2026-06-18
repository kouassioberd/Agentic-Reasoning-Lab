from __future__ import annotations

from .metrics import numeric_exact_match


def judge_answer(prediction: str, expected: str) -> bool:
    return numeric_exact_match(prediction, expected)

