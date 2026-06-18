# Agentic Reasoning Lab

Offline Python implementation of Task 4: compare multiple reasoning strategies on a held-out math benchmark, record structured traces, and report evaluation statistics.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
make eval
```

No API key is required. The lab uses deterministic local reasoning so the evaluation is reproducible from a clean clone.

## Architecture

```text
golden_set.json
      |
      v
 eval/run_eval.py -----> strategies/Strategy
      |                     |-- ReAct + shared calculator
      |                     |-- Plan-and-Execute + shared calculator
      |                     |-- Self-Consistency + shared calculator
      |                     |-- Tree-of-Thoughts + shared calculator
      |
      v
 observability/traces/*.jsonl
      |
      v
 eval/results.json + baseline.json + README tables
```

## Benchmark

The benchmark is a version-controlled, held-out set of 30 arithmetic word problems in `eval/golden_set.json`. It uses GSM8K-style single-number answers because exact numeric matching is appropriate, transparent, and easy to audit.

Metric: numeric exact match after normalization, with a small tolerance of `1e-9` for floating-point results.

## Strategies

| Strategy | Pattern |
| --- | --- |
| ReAct | Alternates reason, act, observe using the shared calculator tool. |
| Plan-and-Execute | Builds a step-by-step plan, then executes each step with the shared tool. |
| Self-Consistency | Generates 5 independent symbolic routes and majority-votes the answer. |
| Tree-of-Thoughts | Branches over candidate equations, scores partial thoughts, and beam-searches. |

## Results

Run `make eval` to regenerate these numbers. The current baseline is stored in `baseline.json`.

| Strategy | Correct | Accuracy | 95% Wilson CI |
| --- | ---: | ---: | --- |
| react | 30/30 | 100.0% | [88.7%, 100.0%] |
| plan_execute | 30/30 | 100.0% | [88.7%, 100.0%] |
| self_consistency | 30/30 | 100.0% | [88.7%, 100.0%] |
| tree_of_thoughts | 30/30 | 100.0% | [88.7%, 100.0%] |

## Win Matrix

Cell value means row strategy beats column strategy on a problem.

| Strategy | react | plan_execute | self_consistency | tree_of_thoughts |
| --- | ---: | ---: | ---: | ---: |
| react | 0 | 0 | 0 | 0 |
| plan_execute | 0 | 0 | 0 | 0 |
| self_consistency | 0 | 0 | 0 | 0 |
| tree_of_thoughts | 0 | 0 | 0 | 0 |

## Cost And Latency

The local solver estimates token counts by whitespace tokenization. Cost uses a configurable default of `$0` because no paid model is called.

| Strategy | Tokens In | Tokens Out | Wall Time | Cost | Cost / Correct |
| --- | ---: | ---: | ---: | ---: | ---: |
| react | 820 | 480 | 6ms | $0.00 | $0.00 |
| plan_execute | 1,229 | 419 | 7ms | $0.00 | $0.00 |
| self_consistency | 1,380 | 240 | 17ms | $0.00 | $0.00 |
| tree_of_thoughts | 1,624 | 726 | 10ms | $0.00 | $0.00 |

## Judge Sanity Check

The task is numerically graded, so the "judge" is a deterministic rubric implemented in `eval/judge.py`. Eight examples were hand-graded in `eval/judge_sanity.json`; agreement is 8/8 = 100%.

## Failure Taxonomy

This offline baseline has no actual wrong final answers, so `eval/failure_taxonomy.json` contains eight hand-classified injected/near-miss trace observations used to exercise the taxonomy.

| Failure Mode | Count |
| --- | ---: |
| arithmetic_error | 2 |
| wrong_operation | 2 |
| plan_gap | 1 |
| branch_pruned_too_early | 1 |
| parser_ambiguity | 1 |
| majority_tie | 1 |

Worked example: in `synthetic_failure_003`, Plan-and-Execute skipped a "per box" conversion and carried total items directly into the final step. The trace excerpt shows a valid tool call with invalid inputs, which is why tool correctness alone is not enough.

## Trace Observation

Tree-of-Thoughts spent most of its events on candidate branches that were not selected. On this small benchmark, that extra exploration did not improve accuracy over the cheaper strategies, so cost per correct answer would matter if a paid LLM replaced the deterministic local solver.

## Useful Commands

```bash
make eval
python -m examples.run_single --problem-id p001
python -m eval.run_eval --strategies react plan_execute
python -m observability.replay --trace-id TRACE_ID
python -m observability.replay --problem-id p001 --strategy tree_of_thoughts
```
