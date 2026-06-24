"""Generate 50+ pSEO pages from catalog."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "services" / "api"))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models import LegalReference, RuleSet
from app.services.seo_service import compose_page_content, upsert_seo_page

from app.data.pseo_catalog import PSEO_CATALOG, reviewed_citation_for_slug


async def generate_pages(session: AsyncSession) -> int:
    ruleset = (
        await session.execute(select(RuleSet).where(RuleSet.status == "active").limit(1))
    ).scalar_one_or_none()
    rule_version = ruleset.version if ruleset else 1

    ref = (
        await session.execute(select(LegalReference).limit(1))
    ).scalar_one_or_none()
    ref_id = ref.id if ref else None

    count = 0
    for industry, industry_name, use_case, use_case_name, risk_hint, citation in PSEO_CATALOG:
        slug = f"{industry}/{use_case}"
        title = f"EU AI Act Compliance for {use_case_name}"
        meta = (
            f"Is {use_case_name.lower()} AI {risk_hint.replace('_', '-')} under the EU AI Act? "
            f"Source-cited guide for {industry_name} vendors."
        )
        content = compose_page_content(
            industry=industry,
            industry_name=industry_name,
            use_case=use_case,
            use_case_name=use_case_name,
            risk_hint=risk_hint,
            citation=f"Regulation (EU) 2024/1689 {reviewed_citation_for_slug(slug)}",
        )
        page_type = "template" if industry == "templates" else "use_case"
        await upsert_seo_page(
            session,
            slug=slug,
            page_type=page_type,
            title=title,
            meta_description=meta,
            content_md=content,
            rule_version=rule_version,
            legal_reference_id=ref_id,
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
