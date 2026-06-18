"""Human-readable labels for assessment answers used in generated documents."""

from __future__ import annotations

from typing import Any

EU_MARKET = {
    "yes": "Operates in the EU today (customers, users, or data subjects in the EU)",
    "planned": "EU sales or users planned within 12 months",
    "no": "No EU market, users, or personal data from the EU",
}

ACTOR_ROLE = {
    "provider": "Provider (develops and places the AI on the market)",
    "deployer": "Deployer (uses a third-party AI in own operations)",
    "distributor": "Distributor (supplies another provider's AI in the EU unchanged)",
    "importer": "Importer (brings a non-EU provider's AI onto the EU market)",
}

USE_CASE = {
    "employment_recruitment": "Hiring and HR (screening, ranking, interviews, performance)",
    "credit_financial": "Credit and finance (scoring, lending, insurance, KYC/AML)",
    "education": "Education (admissions, exams, grading, learner assessment)",
    "healthcare": "Healthcare (triage, diagnosis support, treatment decisions)",
    "customer_support": "Customer chatbot",
    "content_generation": "Synthetic media (images, audio, video, deepfakes)",
    "other": "Other (analytics, search, recommendations, similar)",
}

SYSTEM_FUNCTION = {
    "filter_applications": "Filter or shortlist job applications / CVs",
    "rank_candidates": "Rank or score candidates",
    "evaluate_candidates": "Evaluate interviews, tests, or assessments",
    "monitor_employees": "Monitor or score employee performance",
    "credit_scoring": "Credit scoring or creditworthiness assessment",
    "loan_eligibility": "Approve or deny loans / set loan terms",
    "fraud_detection_only": "Fraud detection only (no credit or pricing decision)",
    "insurance_pricing": "Insurance premium or underwriting risk pricing",
}

RISK_TIER = {
    "prohibited": "Prohibited",
    "high_risk": "High-risk",
    "limited_risk": "Limited-risk (transparency)",
    "minimal_risk": "Minimal risk",
    "needs_review": "Needs expert review",
}

QUESTION_LABELS = {
    "eu_market_exposure": "EU market exposure",
    "actor_role": "Actor role",
    "use_case_category": "Primary use case",
    "affects_natural_persons": "Affects identifiable people",
    "system_function": "System functions",
    "interacts_with_users": "End users interact with AI directly",
    "users_informed_ai": "Users informed they interact with AI",
    "generates_synthetic_media": "Creates synthetic media shown to the public",
}


def _bool_label(value: Any) -> str:
    if value is True:
        return "Yes"
    if value is False:
        return "No"
    return str(value)


def format_answer_value(key: str, value: Any) -> str:
    if value is None:
        return "Not answered"
    if key == "eu_market_exposure":
        return EU_MARKET.get(str(value), str(value))
    if key == "actor_role":
        return ACTOR_ROLE.get(str(value), str(value))
    if key == "use_case_category":
        return USE_CASE.get(str(value), str(value))
    if key == "system_function" and isinstance(value, list):
        return "; ".join(SYSTEM_FUNCTION.get(v, v) for v in value) or "None selected"
    if isinstance(value, bool):
        return _bool_label(value)
    if isinstance(value, list):
        return "; ".join(str(v) for v in value)
    return str(value)


def answer_narrative(answers: dict[str, Any]) -> list[tuple[str, str]]:
    """Ordered question/answer pairs for document appendices."""
    order = [
        "eu_market_exposure",
        "actor_role",
        "use_case_category",
        "affects_natural_persons",
        "system_function",
        "interacts_with_users",
        "users_informed_ai",
        "generates_synthetic_media",
    ]
    rows: list[tuple[str, str]] = []
    for key in order:
        if key in answers:
            label = QUESTION_LABELS.get(key, key.replace("_", " ").title())
            rows.append((label, format_answer_value(key, answers[key])))
    return rows


def risk_tier_label(slug: str) -> str:
    return RISK_TIER.get(slug, slug.replace("_", " ").title())


def actor_role_label(slug: str) -> str:
    return ACTOR_ROLE.get(slug, slug.replace("_", " ").title())


def executive_summary(ctx: dict[str, Any]) -> str:
    """Deterministic narrative from classification facts (not LLM-generated)."""
    system = ctx["system_name"]
    company = ctx["company_name"]
    tier = ctx["risk_tier_label"]
    role = ctx["actor_role_label"]
    use_case = format_answer_value("use_case_category", ctx["answers"].get("use_case_category"))
    eu = format_answer_value("eu_market_exposure", ctx["answers"].get("eu_market_exposure"))

    parts = [
        f"**{system}** ({company}) is classified as **{tier}** under Regulation (EU) 2024/1689.",
        f"The primary actor role for this assessment is **{role}**.",
        f"Declared use case: {use_case}.",
        f"EU exposure: {eu}.",
    ]

    triggered = ctx.get("triggered_rules") or []
    if triggered:
        cites = ", ".join(r["legal_citation"] for r in triggered[:3])
        parts.append(f"Classification is driven by: {cites}.")

    if ctx["risk_tier"] == "high_risk" and ctx["primary_actor_role"] == "provider":
        parts.append(
            "As a high-risk provider, prepare for Articles 9–15 obligations including risk "
            "management, Annex IV technical documentation, logging, deployer transparency, "
            "human oversight, and accuracy or cybersecurity measures."
        )
    elif ctx["risk_tier"] == "limited_risk":
        parts.append(
            "Article 50 transparency obligations apply. Ensure end users are informed when "
            "interacting with AI and label synthetic content where required."
        )
    elif ctx["risk_tier"] == "minimal_risk":
        parts.append(
            "Core high-risk provider duties do not automatically apply, but document your "
            "assessment and monitor regulatory updates."
        )

    return " ".join(parts)
