"""Seed reference data, rules, obligations, and sample SEO page."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import (
    ActorRole,
    DocumentType,
    IndustryDomain,
    LegalReference,
    LegalSource,
    Obligation,
    RiskRule,
    RiskTier,
    RuleSet,
    SEOPage,
)


def seed(session: Session) -> None:
    if session.execute(select(RiskTier).limit(1)).scalar_one_or_none():
        print("Database already seeded — upserting production obligations.")
        from app.scripts.seed_obligations import upsert_production_obligations

        upsert_production_obligations(session)
        session.commit()
        print("Production obligations upserted.")
        return

    tiers = [
        RiskTier(slug="prohibited", name="Prohibited", severity_order=100),
        RiskTier(slug="high_risk", name="High-risk", severity_order=80),
        RiskTier(slug="limited_risk", name="Limited-risk", severity_order=50),
        RiskTier(slug="minimal_risk", name="Minimal-risk", severity_order=10),
        RiskTier(slug="needs_review", name="Needs review", severity_order=90),
    ]
    session.add_all(tiers)
    session.flush()

    tier_by_slug = {t.slug: t for t in tiers}

    roles = [
        ActorRole(slug="provider", name="Provider", description="Develops or places AI on the market"),
        ActorRole(slug="deployer", name="Deployer", description="Uses an AI system under their authority"),
        ActorRole(slug="distributor", name="Distributor"),
        ActorRole(slug="importer", name="Importer"),
    ]
    session.add_all(roles)
    session.flush()
    provider = next(r for r in roles if r.slug == "provider")

    source = LegalSource(
        title="Regulation (EU) 2024/1689 (Artificial Intelligence Act)",
        source_type="regulation",
        jurisdiction="EU",
        url="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
        version_label="2024/1689-consolidated-2026-01",
        status="active",
        effective_date=datetime(2024, 8, 1).date(),
    )
    session.add(source)
    session.flush()

    refs = {
        "annex_iii_4a": LegalReference(
            legal_source_id=source.id,
            annex_number="III",
            section_label="point 4(a)",
            canonical_citation="Regulation (EU) 2024/1689 Annex III point 4(a)",
            reference_text_summary="AI for recruitment or selection of natural persons",
        ),
        "annex_iii_5b": LegalReference(
            legal_source_id=source.id,
            annex_number="III",
            section_label="point 5(b)",
            canonical_citation="Regulation (EU) 2024/1689 Annex III point 5(b)",
            reference_text_summary="AI for evaluating creditworthiness of natural persons",
        ),
        "article_50": LegalReference(
            legal_source_id=source.id,
            article_number="50",
            canonical_citation="Regulation (EU) 2024/1689 Article 50",
            reference_text_summary="Transparency obligations for certain AI systems",
        ),
    }
    session.add_all(refs.values())
    session.flush()

    doc_types = [
        DocumentType(slug="risk_classification_memo", name="Risk Classification Memo", output_formats=["pdf", "md"]),
        DocumentType(slug="annex-iv-technical-documentation", name="Annex IV Technical Documentation", output_formats=["docx"]),
        DocumentType(slug="human-oversight-plan", name="Human Oversight Plan", output_formats=["docx"]),
        DocumentType(slug="evidence-tracker", name="Evidence Tracker", output_formats=["xlsx"]),
    ]
    session.add_all(doc_types)
    session.flush()
    doc_by_slug = {d.slug: d for d in doc_types}

    hr = IndustryDomain(slug="hr-tech", name="HR Tech", description="Human resources technology")
    session.add(hr)
    session.flush()

    ruleset = RuleSet(
        version=1,
        status="active",
        legal_source_version=source.version_label,
        notes="Initial MVP ruleset",
        published_at=datetime.now(timezone.utc),
    )
    session.add(ruleset)
    session.flush()

    rules = [
        RiskRule(
            rule_set_id=ruleset.id,
            rule_code="annex_iii_employment_recruitment_selection",
            name="Annex III employment — recruitment/selection",
            description="System is intended to analyse and filter job applications and evaluate candidates.",
            priority=10,
            phase="high_risk_annex_iii",
            risk_tier_id=tier_by_slug["high_risk"].id,
            legal_reference_id=refs["annex_iii_4a"].id,
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
        ),
        RiskRule(
            rule_set_id=ruleset.id,
            rule_code="annex_iii_credit_scoring",
            name="Annex III — creditworthiness evaluation",
            priority=20,
            phase="high_risk_annex_iii",
            risk_tier_id=tier_by_slug["high_risk"].id,
            legal_reference_id=refs["annex_iii_5b"].id,
            condition_json={
                "all": [
                    {"field": "use_case_category", "operator": "equals", "value": "credit_financial"},
                    {
                        "field": "system_function",
                        "operator": "contains_any",
                        "value": ["credit_scoring", "loan_eligibility", "insurance_pricing"],
                    },
                    {"field": "affects_natural_persons", "operator": "is_true"},
                ]
            },
        ),
        RiskRule(
            rule_set_id=ruleset.id,
            rule_code="limited_risk_chatbot_transparency",
            name="Limited-risk — chatbot transparency",
            priority=30,
            phase="limited_risk",
            risk_tier_id=tier_by_slug["limited_risk"].id,
            legal_reference_id=refs["article_50"].id,
            condition_json={
                "all": [
                    {"field": "use_case_category", "operator": "equals", "value": "customer_support"},
                    {"field": "interacts_with_users", "operator": "is_true"},
                ]
            },
        ),
        RiskRule(
            rule_set_id=ruleset.id,
            rule_code="limited_risk_deepfake",
            name="Limited-risk — synthetic media disclosure",
            priority=40,
            phase="limited_risk",
            risk_tier_id=tier_by_slug["limited_risk"].id,
            legal_reference_id=refs["article_50"].id,
            condition_json={
                "all": [
                    {"field": "use_case_category", "operator": "equals", "value": "content_generation"},
                    {"field": "generates_synthetic_media", "operator": "is_true"},
                ]
            },
        ),
    ]
    session.add_all(rules)

    session.add(
        SEOPage(
            slug="hr-tech/resume-screening",
            page_type="use_case",
            title="EU AI Act Compliance for Resume Screening AI",
            meta_description="Is resume screening AI high-risk under the EU AI Act? Source-cited classification guide for HR-tech vendors.",
            content_md="""## Quick answer

Resume screening and candidate ranking AI is **likely high-risk** under Annex III point 4(a) when it affects natural persons in recruitment.

## Relevant articles

- Regulation (EU) 2024/1689 Annex III point 4(a)

## Documents you likely need

- Risk classification memo
- Annex IV technical documentation skeleton
- Human oversight plan

## Generate your assessment

Run the free AI Act check to classify your specific system.
""",
            canonical_url="http://localhost:3000/eu-ai-act/hr-tech/resume-screening",
            last_reviewed_at=datetime.now(timezone.utc),
            rule_version=1,
            status="active",
        )
    )

    session.commit()
    print("Seed complete.")
    from app.scripts.seed_obligations import upsert_production_obligations

    upsert_production_obligations(session)
    session.commit()
    print("Production obligations upserted.")


def main() -> None:
    engine = create_engine(settings.database_url_sync)
    with Session(engine) as session:
        seed(session)


if __name__ == "__main__":
    main()
