from __future__ import annotations

import argparse
import json

from eval.run_eval import STRATEGY_FACTORIES, load_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Run every strategy on one shared problem.")
    parser.add_argument("--problem-id", default="p001")
    args = parser.parse_args()

    problem = next(item for item in load_dataset() if item["id"] == args.problem_id)
    print(f"Problem {problem['id']}: {problem['question']}")
    print(f"Gold answer: {problem['answer']}\n")

    for name, factory in STRATEGY_FACTORIES.items():
        trace = factory().solve(problem)
        print(f"{name}: answer={trace.answer}, events={len(trace.events)}")
        for event in trace.events:
            print(f"  - {event.step_type}: {event.outputs}")
        if name == "tree_of_thoughts":
            print("  tree:")
            print(json.dumps(trace.metadata["tree"], indent=4))
        print()


if __name__ == "__main__":
    main()

