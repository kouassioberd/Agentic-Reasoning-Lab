from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Callable, Dict, List

from eval.judge import judge_answer
from eval.metrics import wilson_interval, win_matrix
from observability.logger import write_trace
from strategies import (
    PlanAndExecuteStrategy,
    ReActStrategy,
    SelfConsistencyStrategy,
    TreeOfThoughtsStrategy,
)
from tools import Calculator


DATASET_PATH = Path("eval/golden_set.json")
RESULTS_PATH = Path("eval/results.json")
BASELINE_PATH = Path("baseline.json")


def make_calculator() -> Calculator:
    return Calculator()


STRATEGY_FACTORIES: Dict[str, Callable[[], Any]] = {
    "react": lambda: ReActStrategy(make_calculator()),
    "plan_execute": lambda: PlanAndExecuteStrategy(make_calculator()),
    "self_consistency": lambda: SelfConsistencyStrategy(samples=5, calculator=make_calculator()),
    "tree_of_thoughts": lambda: TreeOfThoughtsStrategy(beam_width=2, calculator=make_calculator()),
}


def load_dataset() -> List[Dict[str, Any]]:
    with DATASET_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def summarize(rows: List[Dict[str, Any]], strategies: List[str]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {}
    for strategy in strategies:
        strategy_rows = [row for row in rows if row["strategy"] == strategy]
        correct = sum(1 for row in strategy_rows if row["correct"])
        total = len(strategy_rows)
        ci_low, ci_high = wilson_interval(correct, total)
        tokens_in = sum(int(row["tokens_in"]) for row in strategy_rows)
        tokens_out = sum(int(row["tokens_out"]) for row in strategy_rows)
        wall_ms = sum(float(row["wall_ms"]) for row in strategy_rows)
        summary[strategy] = {
            "correct": correct,
            "total": total,
            "accuracy": correct / total if total else 0,
            "ci95": [ci_low, ci_high],
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "wall_ms": wall_ms,
            "cost_usd": 0.0,
            "cost_per_correct": 0.0,
        }
    return summary


def load_baseline() -> Dict[str, Any]:
    if not BASELINE_PATH.exists():
        return {}
    with BASELINE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the reasoning evaluation harness.")
    parser.add_argument("--strategies", nargs="+", default=list(STRATEGY_FACTORIES))
    args = parser.parse_args()

    problems = load_dataset()
    rows: List[Dict[str, Any]] = []
    print(f"Running {len(args.strategies)} strategies on {len(problems)} problems")

    for strategy_name in args.strategies:
        strategy = STRATEGY_FACTORIES[strategy_name]()
        for problem in problems:
            start = time.perf_counter()
            trace = strategy.solve(problem)
            wall_ms = (time.perf_counter() - start) * 1000
            trace_path = write_trace(trace)
            correct = judge_answer(trace.answer, problem["answer"])
            rows.append(
                {
                    "problem_id": problem["id"],
                    "strategy": strategy_name,
                    "prediction": trace.answer,
                    "expected": problem["answer"],
                    "correct": correct,
                    "trace_id": trace.trace_id,
                    "trace_path": str(trace_path),
                    "tokens_in": sum(event.token_usage["tokens_in"] for event in trace.events),
                    "tokens_out": sum(event.token_usage["tokens_out"] for event in trace.events),
                    "wall_ms": wall_ms,
                }
            )
        print(f"  finished {strategy_name}")

    summary = summarize(rows, args.strategies)
    matrix = win_matrix(rows, args.strategies)
    baseline = load_baseline()
    deltas = {}
    for strategy_name, values in summary.items():
        old = baseline.get("strategies", {}).get(strategy_name, {}).get("accuracy")
        deltas[strategy_name] = None if old is None else values["accuracy"] - old

    output = {
        "metric": "numeric_exact_match",
        "num_problems": len(problems),
        "summary": summary,
        "win_matrix": matrix,
        "baseline_delta": deltas,
        "rows": rows,
    }
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_PATH.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2)

    print("\nFinal metrics")
    for strategy_name, values in summary.items():
        ci_low, ci_high = values["ci95"]
        print(
            f"{strategy_name:18} acc={values['accuracy']:.3f} "
            f"ci95=[{ci_low:.3f}, {ci_high:.3f}] "
            f"delta={deltas[strategy_name]}"
        )
    print(f"\nResults written to {RESULTS_PATH}")


if __name__ == "__main__":
    main()

