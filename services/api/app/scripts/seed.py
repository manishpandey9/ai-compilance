"""Seed reference data, rules, obligations, and sample SEO page."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import (
    ActorRole,
    DocumentType,
    IndustryDomain,
    LegalReference,
    LegalSource,
    RiskRule,
    RiskTier,
    RuleSet,
    SEOPage,
)
from app.rules.conditions import ALLOWED_OPERATORS
from app.rules.priorities import PHASE_ORDER

def _repo_data_path() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "data" / "seeds" / "rules.json"
        if candidate.exists():
            return candidate
    return Path("data/seeds/rules.json").resolve()


RULES_JSON_PATH = _repo_data_path()


def _validate_condition_shape(node: Any) -> None:
    if not isinstance(node, dict):
        raise ValueError("Rule condition node must be an object")

    logical_keys = [key for key in ("all", "any", "none") if key in node]
    if logical_keys:
        if len(logical_keys) != 1 or len(node) != 1:
            raise ValueError("Rule condition logical node must contain exactly one logical key")
        children = node[logical_keys[0]]
        if not isinstance(children, list) or not children:
            raise ValueError("Rule condition logical node must contain a non-empty list")
        for child in children:
            _validate_condition_shape(child)
        return

    if set(node) - {"field", "operator", "value"}:
        raise ValueError("Rule condition leaf contains unsupported keys")
    if not isinstance(node.get("field"), str):
        raise ValueError("Rule condition leaf requires a string field")
    if node.get("operator") not in ALLOWED_OPERATORS:
        raise ValueError(f"Unsupported condition operator: {node.get('operator')}")


def _load_seed_rules() -> list[dict[str, Any]]:
    payload = json.loads(RULES_JSON_PATH.read_text())
    rules = payload.get("rules")
    if not isinstance(rules, list) or not rules:
        raise ValueError("rules.json must contain a non-empty rules array")

    seen_codes: set[str] = set()
    required = {
        "rule_code",
        "name",
        "priority",
        "phase",
        "risk_tier_slug",
        "legal_reference_key",
        "condition_json",
    }
    for row in rules:
        if not isinstance(row, dict):
            raise ValueError("Each rule row must be an object")
        missing = required - set(row)
        if missing:
            raise ValueError(f"Rule row missing keys: {sorted(missing)}")
        if row["rule_code"] in seen_codes:
            raise ValueError(f"Duplicate rule_code: {row['rule_code']}")
        seen_codes.add(row["rule_code"])
        if row["phase"] not in PHASE_ORDER:
            raise ValueError(f"Unsupported rule phase: {row['phase']}")
        _validate_condition_shape(row["condition_json"])
    return rules


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

    hr = IndustryDomain(slug="hr-tech", name="HR Tech", description="Human resources technology")
    session.add(hr)
    session.flush()

    ruleset = RuleSet(
        version=1,
        status="active",
        legal_source_version=source.version_label,
        notes="Initial MVP ruleset",
        published_at=datetime.now(UTC),
    )
    session.add(ruleset)
    session.flush()

    rules = [
        RiskRule(
            rule_set_id=ruleset.id,
            rule_code=row["rule_code"],
            name=row["name"],
            description=row.get("description"),
            priority=row["priority"],
            phase=row["phase"],
            risk_tier_id=tier_by_slug[row["risk_tier_slug"]].id,
            legal_reference_id=refs[row["legal_reference_key"]].id,
            condition_json=row["condition_json"],
        )
        for row in _load_seed_rules()
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
            last_reviewed_at=datetime.now(UTC),
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
