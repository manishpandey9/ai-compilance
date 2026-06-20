"""Prepare assessment answers for deterministic classification."""

from __future__ import annotations

from typing import Any


EU_EXPOSURE_VALUES = {"yes", "planned", True}
REVIEW_CATEGORIES_WHEN_PEOPLE_AFFECTED = {"education", "healthcare", "other"}
SUPPORTED_HR_FUNCTIONS = {"filter_applications", "rank_candidates", "evaluate_candidates"}
SUPPORTED_FINANCE_FUNCTIONS = {"credit_scoring", "loan_eligibility", "insurance_pricing"}


def _values(value: Any) -> set[str]:
    if isinstance(value, list):
        return {str(item) for item in value}
    if value is None:
        return set()
    return {str(value)}


def prepare_classification_facts(answers: dict[str, Any]) -> dict[str, Any]:
    """Add review flags for high-stakes areas not yet covered by rules."""
    facts = dict(answers)

    if facts.get("eu_market_exposure") not in EU_EXPOSURE_VALUES:
        return facts
    if facts.get("affects_natural_persons") is not True:
        return facts

    category = facts.get("use_case_category")
    functions = _values(facts.get("system_function"))

    if category in REVIEW_CATEGORIES_WHEN_PEOPLE_AFFECTED:
        facts["uncertain_high_risk"] = True
    elif category == "employment_recruitment" and not functions.intersection(SUPPORTED_HR_FUNCTIONS):
        facts["uncertain_high_risk"] = True
    elif category == "credit_financial" and not functions.intersection(SUPPORTED_FINANCE_FUNCTIONS):
        facts["uncertain_high_risk"] = True

    return facts

