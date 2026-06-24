"""Generate 50+ pSEO pages from catalog."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "services" / "api"))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.data.pseo_catalog import PSEO_CATALOG, reviewed_citation_for_slug
from app.models import LegalReference, RuleSet
from app.services.seo_service import compose_page_content, upsert_seo_page

CITATION_REFERENCE_MAP = {
    "Annex III point 4(a)": ["Regulation (EU) 2024/1689 Annex III point 4(a)"],
    "Annex III point 4(b)": ["Regulation (EU) 2024/1689 Annex III point 4(a)"],
    "Annex III point 5(b)": ["Regulation (EU) 2024/1689 Annex III point 5(b)"],
    "Article 50": ["Regulation (EU) 2024/1689 Article 50"],
    "Article 14": ["Regulation (EU) 2024/1689 Article 14"],
    "Article 27": ["Regulation (EU) 2024/1689 Article 27"],
    "Annex IV": [
        "Regulation (EU) 2024/1689 Annex IV",
        "Regulation (EU) 2024/1689 Article 11",
    ],
    "Article 16 / Article 26": [
        "Regulation (EU) 2024/1689 Article 16",
        "Regulation (EU) 2024/1689 Article 26",
    ],
}


def citation_reference_candidates(citation: str) -> list[str]:
    return CITATION_REFERENCE_MAP.get(citation, [])


def _page_type(industry: str) -> str:
    if industry == "templates":
        return "template"
    if industry == "roles":
        return "role"
    return "use_case"


def _title(industry: str, use_case_name: str) -> str:
    if industry == "templates":
        return f"EU AI Act {use_case_name}"
    if industry == "roles":
        return f"EU AI Act {use_case_name}"
    return f"EU AI Act Compliance for {use_case_name}"


def _meta(industry_name: str, use_case_name: str, risk_hint: str) -> str:
    if industry_name == "Templates":
        return (
            f"Source-cited EU AI Act {use_case_name.lower()} guidance for preparing "
            "evidence-pack drafts."
        )
    if industry_name == "Roles":
        return (
            f"Provider vs deployer duties under the EU AI Act for {use_case_name.lower()}, "
            "with Article 16 and Article 26 context."
        )
    return (
        f"Is {use_case_name.lower()} AI {risk_hint.replace('_', '-')} under the EU AI Act? "
        f"Source-cited guide for {industry_name} vendors."
    )


async def _reference_ids_for_citation(session: AsyncSession, citation: str) -> list[int]:
    candidates = citation_reference_candidates(citation)
    if not candidates:
        return []

    result = await session.execute(
        select(LegalReference).where(LegalReference.canonical_citation.in_(candidates))
    )
    by_citation = {ref.canonical_citation: ref.id for ref in result.scalars().all()}
    return [by_citation[candidate] for candidate in candidates if candidate in by_citation]


async def generate_pages(session: AsyncSession) -> int:
    ruleset = (
        await session.execute(select(RuleSet).where(RuleSet.status == "active").limit(1))
    ).scalar_one_or_none()
    rule_version = ruleset.version if ruleset else 1

    count = 0
    for industry, industry_name, use_case, use_case_name, risk_hint, citation in PSEO_CATALOG:
        slug = f"{industry}/{use_case}"
        title = _title(industry, use_case_name)
        meta = _meta(industry_name, use_case_name, risk_hint)
        content = compose_page_content(
            industry=industry,
            industry_name=industry_name,
            use_case=use_case,
            use_case_name=use_case_name,
            risk_hint=risk_hint,
            citation=f"Regulation (EU) 2024/1689 {reviewed_citation_for_slug(slug)}",
        )
        await upsert_seo_page(
            session,
            slug=slug,
            page_type=_page_type(industry),
            title=title,
            meta_description=meta,
            content_md=content,
            rule_version=rule_version,
            legal_reference_ids=await _reference_ids_for_citation(session, citation),
            use_case_name=use_case_name,
            risk_hint=risk_hint,
        )
        count += 1

    await session.commit()
    return count


async def main() -> None:
    engine = create_async_engine(settings.database_url)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        n = await generate_pages(session)
    print(f"Generated/updated {n} pSEO pages.")


if __name__ == "__main__":
    asyncio.run(main())
