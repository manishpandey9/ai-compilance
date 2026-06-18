"""Pure deterministic rule engine — no I/O."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from app.rules.conditions import ConditionEvaluationError, evaluate_condition
from app.rules.priorities import PHASE_ORDER, REQUIRED_FACT_KEYS


@dataclass
class RuleRecord:
    rule_code: str
    name: str
    phase: str
    priority: int
    risk_tier_slug: str
    condition_json: dict[str, Any]
    legal_citation: str
    rationale_template: str


@dataclass
class TriggeredRule:
    rule_code: str
    source: str
    rationale: str
    phase: str


@dataclass
class ClassificationOutput:
    classification_status: str
    risk_tier: str | None
    confidence: str | None
    primary_actor_role: str | None
    secondary_actor_roles: list[str]
    triggered_rules: list[TriggeredRule]
    missing_fields: list[str]
    edge_flags: list[str] = field(default_factory=list)
    result_json: dict[str, Any] = field(default_factory=dict)


def _missing_required_facts(facts: dict[str, Any]) -> list[str]:
    missing = []
    for key in REQUIRED_FACT_KEYS:
        if key not in facts or facts[key] is None:
            missing.append(key)
    return missing


def _has_eu_exposure(facts: dict[str, Any]) -> bool:
    exposure = facts.get("eu_market_exposure")
    return exposure in {"yes", "planned", True}


def _infer_actor_role(facts: dict[str, Any]) -> tuple[str, list[str]]:
    role = facts.get("actor_role", "provider")
    secondary: list[str] = []
    if role == "provider" and facts.get("deployed_internally"):
        secondary.append("deployer_when_used_internally")
    return role, secondary


def _build_rationale(rule: RuleRecord, facts: dict[str, Any]) -> str:
    if rule.rationale_template:
        try:
            return rule.rationale_template.format(**facts)
        except (KeyError, ValueError):
            pass
    return rule.name


def classify(
    facts: dict[str, Any],
    rules: list[RuleRecord],
    *,
    now: date | None = None,
    rule_version: int = 1,
    source_version: str = "unknown",
) -> ClassificationOutput:
    """Pure classification: same inputs always produce identical output."""
    _ = now  # reserved for effective_from/to filtering at service layer
    _ = rule_version
    _ = source_version

    missing = _missing_required_facts(facts)
    if missing:
        return ClassificationOutput(
            classification_status="insufficient_information",
            risk_tier=None,
            confidence=None,
            primary_actor_role=None,
            secondary_actor_roles=[],
            triggered_rules=[],
            missing_fields=missing,
            result_json={"missing_fields": missing},
        )

    if not _has_eu_exposure(facts):
        primary_role, secondary_roles = _infer_actor_role(facts)
        return ClassificationOutput(
            classification_status="classified",
            risk_tier="minimal_risk",
            confidence="high",
            primary_actor_role=primary_role,
            secondary_actor_roles=secondary_roles,
            triggered_rules=[],
            missing_fields=[],
            edge_flags=["outside_eu_scope"],
            result_json={"note": "No EU market exposure indicated; minimal obligations may still apply indirectly."},
        )

    primary_role, secondary_roles = _infer_actor_role(facts)
    triggered: list[TriggeredRule] = []
    matched_tier: str | None = None

    rules_by_phase: dict[str, list[RuleRecord]] = {p: [] for p in PHASE_ORDER}
    for rule in sorted(rules, key=lambda r: (PHASE_ORDER.index(r.phase) if r.phase in PHASE_ORDER else 99, r.priority, r.rule_code)):
        if rule.phase in rules_by_phase:
            rules_by_phase[rule.phase].append(rule)

    for phase in PHASE_ORDER:
        for rule in rules_by_phase[phase]:
            try:
                if evaluate_condition(rule.condition_json, facts):
                    triggered.append(
                        TriggeredRule(
                            rule_code=rule.rule_code,
                            source=rule.legal_citation,
                            rationale=_build_rationale(rule, facts),
                            phase=phase,
                        )
                    )
                    if matched_tier is None:
                        matched_tier = rule.risk_tier_slug
            except ConditionEvaluationError:
                continue

        if matched_tier == "prohibited":
            break
        if matched_tier in {"high_risk"}:
            break

    if matched_tier == "prohibited":
        confidence = "high"
    elif matched_tier == "high_risk":
        confidence = "high" if len(triggered) == 1 else "medium"
    elif matched_tier == "limited_risk":
        confidence = "medium"
    elif matched_tier == "minimal_risk":
        confidence = "high"
    else:
        if facts.get("uncertain_high_risk"):
            return ClassificationOutput(
                classification_status="needs_expert_review",
                risk_tier="high_risk",
                confidence="low",
                primary_actor_role=primary_role,
                secondary_actor_roles=secondary_roles,
                triggered_rules=triggered,
                missing_fields=[],
                edge_flags=["possibly_high_risk"],
                result_json={"triggered_rules": [t.__dict__ for t in triggered]},
            )
        matched_tier = "minimal_risk"
        confidence = "medium"

    return ClassificationOutput(
        classification_status="classified",
        risk_tier=matched_tier,
        confidence=confidence,
        primary_actor_role=primary_role,
        secondary_actor_roles=secondary_roles,
        triggered_rules=triggered,
        missing_fields=[],
        result_json={
            "triggered_rules": [t.__dict__ for t in triggered],
            "facts_used": {k: facts[k] for k in REQUIRED_FACT_KEYS if k in facts},
        },
    )
