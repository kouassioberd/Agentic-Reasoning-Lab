from strategies import (
    PlanAndExecuteStrategy,
    ReActStrategy,
    SelfConsistencyStrategy,
    TreeOfThoughtsStrategy,
)


PROBLEM = {
    "id": "demo",
    "question": "Mia has 12 stickers, buys 8 more, and gives 5 away.",
    "answer": "15",
    "expression": "12 + 8 - 5",
    "distractors": ["12 + 8 + 5", "12 - 8 - 5"],
}


def test_all_strategies_solve_demo_problem():
    for cls in [ReActStrategy, PlanAndExecuteStrategy, SelfConsistencyStrategy, TreeOfThoughtsStrategy]:
        trace = cls().solve(PROBLEM)
        assert trace.answer == "15"
        assert trace.events

