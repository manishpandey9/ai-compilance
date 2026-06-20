from app.services.assessment_facts import prepare_classification_facts


def test_supported_hr_recruitment_facts_do_not_force_review():
    facts = prepare_classification_facts(
        {
            "eu_market_exposure": "yes",
            "actor_role": "provider",
            "use_case_category": "employment_recruitment",
            "affects_natural_persons": True,
            "system_function": ["filter_applications"],
        }
    )

    assert "uncertain_high_risk" not in facts


def test_unsupported_hr_function_is_review_territory():
    facts = prepare_classification_facts(
        {
            "eu_market_exposure": "yes",
            "actor_role": "provider",
            "use_case_category": "employment_recruitment",
            "affects_natural_persons": True,
            "system_function": ["monitor_employees"],
        }
    )

    assert facts["uncertain_high_risk"] is True


def test_education_and_healthcare_people_impact_are_review_territory():
    for category in ["education", "healthcare"]:
        facts = prepare_classification_facts(
            {
                "eu_market_exposure": "yes",
                "actor_role": "provider",
                "use_case_category": category,
                "affects_natural_persons": True,
            }
        )

        assert facts["uncertain_high_risk"] is True


def test_no_eu_exposure_does_not_force_review():
    facts = prepare_classification_facts(
        {
            "eu_market_exposure": "no",
            "actor_role": "provider",
            "use_case_category": "education",
            "affects_natural_persons": True,
        }
    )

    assert "uncertain_high_risk" not in facts

