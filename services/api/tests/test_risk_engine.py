"""Rule engine golden tests — PRD §21.1 fixtures."""

from app.rules.engine import RuleRecord, classify

HR_RULE = RuleRecord(
    rule_code="annex_iii_employment_recruitment_selection",
    name="Annex III employment",
    phase="high_risk_annex_iii",
    priority=10,
    risk_tier_slug="high_risk",
    condition_json={
        "all": [
            {"field": "use_case_category", "operator": "equals", "value": "employment_recruitment"},
            {
                "field": "system_function",
                "operator": "contains_any",
                "value": ["filter_applications", "rank_candidates", "evaluate_candidates"],
            },
            {"field": "affects_natural_persons", "operator": "is_true"},
        ]
    },
    legal_citation="Regulation (EU) 2024/1689 Annex III point 4(a)",
    rationale_template="System analyses job applications for recruitment.",
)

CREDIT_RULE = RuleRecord(
    rule_code="annex_iii_credit_scoring",
    name="Annex III credit",
    phase="high_risk_annex_iii",
    priority=20,
    risk_tier_slug="high_risk",
    condition_json={
        "all": [
            {"field": "use_case_category", "operator": "equals", "value": "credit_financial"},
            {"field": "system_function", "operator": "contains_any", "value": ["credit_scoring", "loan_eligibility"]},
            {"field": "affects_natural_persons", "operator": "is_true"},
        ]
    },
    legal_citation="Regulation (EU) 2024/1689 Annex III point 5(b)",
    rationale_template="Evaluates creditworthiness.",
)

CHATBOT_RULE = RuleRecord(
    rule_code="limited_risk_chatbot",
    name="Chatbot transparency",
    phase="limited_risk",
    priority=30,
    risk_tier_slug="limited_risk",
    condition_json={
        "all": [
            {"field": "use_case_category", "operator": "equals", "value": "customer_support"},
            {"field": "interacts_with_users", "operator": "is_true"},
        ]
    },
    legal_citation="Regulation (EU) 2024/1689 Article 50",
    rationale_template="Chatbot interacts with users.",
)

RULES = [HR_RULE, CREDIT_RULE, CHATBOT_RULE]


def test_resume_screening_high_risk():
    facts = {
        "eu_market_exposure": "yes",
        "actor_role": "provider",
        "use_case_category": "employment_recruitment",
        "affects_natural_persons": True,
        "system_function": ["filter_applications", "rank_candidates"],
    }
    result = classify(facts, RULES)
    assert result.classification_status == "classified"
    assert result.risk_tier == "high_risk"
    assert any(t.rule_code == "annex_iii_employment_recruitment_selection" for t in result.triggered_rules)


def test_credit_scoring_high_risk():
    facts = {
        "eu_market_exposure": "yes",
        "actor_role": "provider",
        "use_case_category": "credit_financial",
        "affects_natural_persons": True,
        "system_function": ["credit_scoring"],
    }
    result = classify(facts, RULES)
    assert result.risk_tier == "high_risk"


def test_customer_chatbot_limited_risk():
    facts = {
        "eu_market_exposure": "yes",
        "actor_role": "provider",
        "use_case_category": "customer_support",
        "affects_natural_persons": True,
        "interacts_with_users": True,
    }
    result = classify(facts, RULES)
    assert result.risk_tier == "limited_risk"


def test_spam_filter_minimal_risk():
    facts = {
        "eu_market_exposure": "yes",
        "actor_role": "provider",
        "use_case_category": "other",
        "affects_natural_persons": False,
    }
    result = classify(facts, RULES)
    assert result.risk_tier == "minimal_risk"


def test_insufficient_information():
    facts = {"eu_market_exposure": "yes"}
    result = classify(facts, RULES)
    assert result.classification_status == "insufficient_information"
    assert "use_case_category" in result.missing_fields


def test_no_eu_exposure():
    facts = {
        "eu_market_exposure": "no",
        "actor_role": "provider",
        "use_case_category": "employment_recruitment",
        "affects_natural_persons": True,
    }
    result = classify(facts, RULES)
    assert result.risk_tier == "minimal_risk"
    assert "outside_eu_scope" in result.edge_flags
