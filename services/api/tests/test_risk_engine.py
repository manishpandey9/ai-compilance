"""Rule engine fixture tests — these gate rule publishing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.rules.engine import RuleRecord, classify
from app.services.assessment_facts import prepare_classification_facts

ROOT = Path(__file__).resolve().parents[3]
RULES_PATH = ROOT / "data" / "seeds" / "rules.json"
FIXTURE_DIR = Path(__file__).parent / "fixtures"

LEGAL_CITATIONS = {
    "annex_iii_4a": "Regulation (EU) 2024/1689 Annex III point 4(a)",
    "annex_iii_5b": "Regulation (EU) 2024/1689 Annex III point 5(b)",
    "article_50": "Regulation (EU) 2024/1689 Article 50",
}


def _load_rules() -> list[RuleRecord]:
    seed = json.loads(RULES_PATH.read_text())
    return [
        RuleRecord(
            rule_code=row["rule_code"],
            name=row["name"],
            phase=row["phase"],
            priority=row["priority"],
            risk_tier_slug=row["risk_tier_slug"],
            condition_json=row["condition_json"],
            legal_citation=LEGAL_CITATIONS[row["legal_reference_key"]],
            rationale_template=row.get("rationale_template") or row["name"],
        )
        for row in seed["rules"]
    ]


def _fixture_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for path in sorted(FIXTURE_DIR.glob("*.json")):
        cases.extend(json.loads(path.read_text())["cases"])
    return cases


def test_rule_fixture_suite_has_coverage():
    names = {case["name"] for case in _fixture_cases()}

    assert "hr_recruitment_high_risk" in names
    assert "credit_scoring_high_risk" in names
    assert "chatbot_transparency_limited_risk" in names
    assert "synthetic_media_limited_risk" in names
    assert "outside_eu_scope" in names
    assert "missing_required_facts" in names
    assert "unsupported_healthcare_routes_to_expert_review" in names
    assert "article_6_3_downgrade_without_profiling" in names
    assert "article_6_3_profiling_override_remains_high_risk" in names


def test_rule_engine_fixtures():
    rules = _load_rules()

    for case in _fixture_cases():
        facts = case["facts"]
        if case.get("prepare_facts"):
            facts = prepare_classification_facts(facts)

        result = classify(facts, rules)
        expected = case["expected"]

        assert result.classification_status == expected["classification_status"], case["name"]
        assert result.risk_tier == expected.get("risk_tier"), case["name"]
        assert result.confidence == expected.get("confidence"), case["name"]

        expected_missing = expected.get("missing_fields")
        if expected_missing is not None:
            assert sorted(result.missing_fields) == sorted(expected_missing), case["name"]

        for flag in expected.get("edge_flags_contains", []):
            assert flag in result.edge_flags, case["name"]

        triggered_codes = {rule.rule_code for rule in result.triggered_rules}
        assert triggered_codes == set(expected.get("triggered_rule_codes", [])), case["name"]
