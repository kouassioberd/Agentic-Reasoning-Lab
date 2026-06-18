from __future__ import annotations

import math
from typing import Dict, Iterable, List, Optional, Tuple


def normalize_number(value: str) -> Optional[float]:
    try:
        return float(str(value).strip().replace(",", ""))
    except ValueError:
        return None


def numeric_exact_match(prediction: str, expected: str, tolerance: float = 1e-9) -> bool:
    pred = normalize_number(prediction)
    gold = normalize_number(expected)
    if pred is None or gold is None:
        return str(prediction).strip() == str(expected).strip()
    return abs(pred - gold) <= tolerance


def wilson_interval(correct: int, total: int, z: float = 1.96) -> Tuple[float, float]:
    if total == 0:
        return (0.0, 0.0)
    phat = correct / total
    denom = 1 + z * z / total
    center = (phat + z * z / (2 * total)) / denom
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


def win_matrix(rows: List[Dict[str, object]], strategies: Iterable[str]) -> Dict[str, Dict[str, int]]:
    names = list(strategies)
    matrix = {left: {right: 0 for right in names} for left in names}
    by_problem: Dict[str, Dict[str, bool]] = {}
    for row in rows:
        by_problem.setdefault(str(row["problem_id"]), {})[str(row["strategy"])] = bool(row["correct"])
    for outcomes in by_problem.values():
        for left in names:
            for right in names:
                if outcomes.get(left, False) and not outcomes.get(right, False):
                    matrix[left][right] += 1
    return matrix
