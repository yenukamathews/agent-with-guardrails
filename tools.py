
import ast
import operator
from typing import Any

from guards import validate_sql


# Allow only basic arithmetic operations.
_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def calculator(expression: str) -> float | int:
    """Safely evaluate a basic arithmetic expression."""

    if not isinstance(expression, str) or not expression.strip():
        raise ValueError("Expression cannot be empty.")

    if len(expression) > 100:
        raise ValueError("Expression is too long.")

    def evaluate(node: ast.AST) -> Any:
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp):
            operation = _ALLOWED_OPERATORS.get(type(node.op))
            if operation is None:
                raise ValueError("Operator not allowed.")

            left = evaluate(node.left)
            right = evaluate(node.right)

            # Prevent huge exponent calculations.
            if isinstance(node.op, ast.Pow) and abs(right) > 10:
                raise ValueError("Exponent is too large.")

            result = operation(left, right)

            if isinstance(result, complex):
                raise ValueError("Complex results are not supported.")

            if isinstance(result, float) and not __import__("math").isfinite(result):
                raise ValueError("Result must be finite.")

            if abs(result) > 10**100:
                raise ValueError("Result is too large.")

            return result

        if isinstance(node, ast.UnaryOp):
            operation = _ALLOWED_OPERATORS.get(type(node.op))
            if operation is None:
                raise ValueError("Unary operator not allowed.")
            return operation(evaluate(node.operand))

        raise ValueError("Only arithmetic expressions are allowed.")

    try:
        tree = ast.parse(expression, mode="eval")
        return evaluate(tree)
    except (SyntaxError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError("Invalid arithmetic expression.") from exc


def sql_tool(query: str) -> dict:
    """Validate SQL before returning it for a future read-only database."""

    safe_query = validate_sql(query)

    # No database is connected yet. This tool does not execute SQL.
    return {
        "status": "validated",
        "query": safe_query,
        "message": "SQL passed basic validation; no database was queried.",
    }
