from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json
from typing import Iterable

from strategies import Trace


TRACE_DIR = Path("observability/traces")


def write_trace(trace: Trace, trace_dir: Path = TRACE_DIR) -> Path:
    trace_dir.mkdir(parents=True, exist_ok=True)
    path = trace_dir / f"{trace.trace_id}.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        header = {
            "trace_id": trace.trace_id,
            "strategy": trace.strategy,
            "problem_id": trace.problem_id,
            "answer": trace.answer,
            "metadata": trace.metadata,
        }
        handle.write(json.dumps({"type": "trace", **header}) + "\n")
        for event in trace.events:
            handle.write(json.dumps({"type": "event", **asdict(event)}) + "\n")
    return path


def iter_trace_files(trace_dir: Path = TRACE_DIR) -> Iterable[Path]:
    if not trace_dir.exists():
        return []
    return trace_dir.glob("*.jsonl")

