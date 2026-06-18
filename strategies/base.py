from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List
import time
import uuid


@dataclass
class StepEvent:
    strategy: str
    problem_id: str
    step_type: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    token_usage: Dict[str, int]
    latency_ms: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class Trace:
    trace_id: str
    strategy: str
    problem_id: str
    answer: str
    events: List[StepEvent]
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, strategy: str, problem_id: str) -> "Trace":
        return cls(
            trace_id=str(uuid.uuid4()),
            strategy=strategy,
            problem_id=problem_id,
            answer="",
            events=[],
        )

    def add_event(
        self,
        step_type: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        start_time: float,
    ) -> None:
        prompt_text = " ".join(str(v) for v in inputs.values())
        output_text = " ".join(str(v) for v in outputs.values())
        self.events.append(
            StepEvent(
                strategy=self.strategy,
                problem_id=self.problem_id,
                step_type=step_type,
                inputs=inputs,
                outputs=outputs,
                token_usage={
                    "tokens_in": len(prompt_text.split()),
                    "tokens_out": len(output_text.split()),
                },
                latency_ms=(time.perf_counter() - start_time) * 1000,
            )
        )


class Strategy:
    name: str

    def solve(self, problem: Dict[str, Any]) -> Trace:  # pragma: no cover - interface method
        raise NotImplementedError
