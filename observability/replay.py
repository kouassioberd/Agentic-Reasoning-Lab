from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from eval.run_eval import STRATEGY_FACTORIES, load_dataset


def find_trace(trace_id: str, trace_dir: Path = Path("observability/traces")) -> Dict[str, Any]:
    path = trace_dir / f"{trace_id}.jsonl"
    if not path.exists():
        raise FileNotFoundError(f"Trace not found: {trace_id}")
    with path.open("r", encoding="utf-8") as handle:
        return json.loads(handle.readline())


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay a single problem from a trace or explicit problem id.")
    parser.add_argument("--trace-id")
    parser.add_argument("--problem-id")
    parser.add_argument("--strategy")
    args = parser.parse_args()

    header: Dict[str, Any] = {}
    if args.trace_id:
        header = find_trace(args.trace_id)

    problem_id = args.problem_id or header.get("problem_id")
    strategy_name = args.strategy or header.get("strategy")
    if not problem_id or not strategy_name:
        raise SystemExit("Provide --trace-id or both --problem-id and --strategy")

    problems: List[Dict[str, Any]] = load_dataset()
    problem = next(item for item in problems if item["id"] == problem_id)
    trace = STRATEGY_FACTORIES[strategy_name]().solve(problem)
    print(json.dumps({
        "original_trace_id": args.trace_id,
        "new_trace_id": trace.trace_id,
        "problem_id": problem_id,
        "strategy": strategy_name,
        "answer": trace.answer,
        "events": len(trace.events),
    }, indent=2))


if __name__ == "__main__":
    main()

