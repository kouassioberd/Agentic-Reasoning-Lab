from __future__ import annotations

import ast
import operator
from dataclasses import dataclass
from typing import Any, Callable, Dict


OPS: Dict[type, Callable[[Any, Any], Any]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def safe_eval(expression: str) -> float:
    node = ast.parse(expression, mode="eval")
    return float(_eval_node(node.body))


def _eval_node(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval_node(node.operand)
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


@dataclass
class Calculator:
    name: str = "calculator"

    def run(self, expression: str) -> str:
        value = safe_eval(expression)
        if value.is_integer():
            return str(int(value))
        return str(value)
