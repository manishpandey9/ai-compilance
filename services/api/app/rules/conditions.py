"""Sandboxed JSON boolean AST evaluator — no eval()."""

from __future__ import annotations

from typing import Any

ALLOWED_OPERATORS = frozenset(
    {
        "equals",
        "not_equals",
        "in",
        "not_in",
        "contains_any",
        "contains_all",
        "is_true",
        "is_false",
        "exists",
        "not_exists",
    }
)


class ConditionEvaluationError(ValueError):
    pass


def _get_field(facts: dict[str, Any], field: str) -> Any:
    if "." in field:
        parts = field.split(".")
        value: Any = facts
        for part in parts:
            if not isinstance(value, dict) or part not in value:
                return None
            value = value[part]
        return value
    return facts.get(field)


def _evaluate_leaf(node: dict[str, Any], facts: dict[str, Any]) -> bool:
    operator = node.get("operator")
    if operator not in ALLOWED_OPERATORS:
        raise ConditionEvaluationError(f"Unsupported operator: {operator}")

    field = node.get("field")
    value = node.get("value")

    if operator == "exists":
        return _get_field(facts, field) is not None
    if operator == "not_exists":
        return _get_field(facts, field) is None
    if operator == "is_true":
        return _get_field(facts, field) is True
    if operator == "is_false":
        return _get_field(facts, field) is False

    actual = _get_field(facts, field)

    if operator == "equals":
        return actual == value
    if operator == "not_equals":
        return actual != value
    if operator == "in":
        if not isinstance(value, list):
            raise ConditionEvaluationError("'in' operator requires list value")
        return actual in value
    if operator == "not_in":
        if not isinstance(value, list):
            raise ConditionEvaluationError("'not_in' operator requires list value")
        return actual not in value
    if operator == "contains_any":
        if not isinstance(actual, list) or not isinstance(value, list):
            return False
        return any(item in actual for item in value)
    if operator == "contains_all":
        if not isinstance(actual, list) or not isinstance(value, list):
            return False
        return all(item in actual for item in value)

    raise ConditionEvaluationError(f"Unhandled operator: {operator}")


def evaluate_condition(node: dict[str, Any], facts: dict[str, Any]) -> bool:
    """Evaluate a condition AST node against assessment facts."""
    if not isinstance(node, dict):
        raise ConditionEvaluationError("Condition node must be an object")

    if "all" in node:
        children = node["all"]
        if not isinstance(children, list) or not children:
            raise ConditionEvaluationError("'all' requires a non-empty array")
        return all(evaluate_condition(child, facts) for child in children)

    if "any" in node:
        children = node["any"]
        if not isinstance(children, list) or not children:
            raise ConditionEvaluationError("'any' requires a non-empty array")
        return any(evaluate_condition(child, facts) for child in children)

    if "none" in node:
        children = node["none"]
        if not isinstance(children, list) or not children:
            raise ConditionEvaluationError("'none' requires a non-empty array")
        return not any(evaluate_condition(child, facts) for child in children)

    if "operator" in node:
        return _evaluate_leaf(node, facts)

    raise ConditionEvaluationError("Condition node must have 'all', 'any', 'none', or 'operator'")
