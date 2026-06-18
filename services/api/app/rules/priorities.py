"""Rule execution phase ordering."""

from __future__ import annotations

PHASE_ORDER = [
    "prohibited",
    "high_risk_annex_i",
    "high_risk_annex_iii",
    "limited_risk",
    "minimal_risk",
]

REQUIRED_FACT_KEYS = frozenset(
    {
        "eu_market_exposure",
        "use_case_category",
        "affects_natural_persons",
        "actor_role",
    }
)
