"""pSEO page composition from structured catalog data."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import LegalReference, SEOPage, SEOPageReference

_RISK_COPY: dict[str, dict[str, str]] = {
    "high_risk": {
        "tier_label": "high-risk",
        "legal_basis": (
            "Under **Article 6(2)** of Regulation (EU) 2024/1689, AI systems listed in "
            "**Annex III** are high-risk unless the Article 6(3) narrow exception applies "
            "(and profiling always remains high-risk). Provider obligations include risk "
            "management (Art. 9), data governance (Art. 10), technical documentation (Art. 11 "
            "/ Annex IV), record-keeping (Art. 12), transparency to deployers (Art. 13), human "
            "oversight (Art. 14), and accuracy/robustness (Art. 15). Enforcement for Annex III "
            "systems: **2 August 2026** (with some extensions for embedded products)."
        ),
        "documents": (
            "- Annex IV technical documentation outline\n"
            "- Risk management system summary\n"
            "- Human oversight plan\n"
            "- Conformity assessment / CE marking checklist (where applicable)\n"
            "- Fundamental rights impact assessment (FRIA) when deployer is a public body (Art. 27)"
        ),
    },
    "limited_risk": {
        "tier_label": "limited-risk (transparency)",
        "legal_basis": (
            "**Article 50** transparency obligations apply to certain AI systems, such as "
            "chatbots that interact with people, emotion-recognition or biometric categorisation "
            "in specified contexts, and AI-generated or manipulated content (deepfakes) that must "
            "be disclosed. These systems are not Annex III high-risk by default, but you must "
            "inform users and label synthetic content clearly."
        ),
        "documents": (
            "- Transparency / disclosure notice for end users\n"
            "- Content labeling policy for synthetic media\n"
            "- Internal record of AI interaction design"
        ),
    },
    "minimal_risk": {
        "tier_label": "minimal risk",
        "legal_basis": (
            "Many AI systems fall outside prohibited practices (Art. 5), Annex III high-risk "
            "categories, and Art. 50 transparency triggers. You should still document your "
            "voluntary codes of conduct and monitor regulatory updates. Core high-risk "
            "provider duties do not automatically apply."
        ),
        "documents": (
            "- Optional AI inventory entry\n"
            "- Basic model / data documentation for internal governance"
        ),
    },
    "prohibited": {
        "tier_label": "prohibited",
        "legal_basis": (
            "**Article 5** prohibits certain AI practices outright (e.g. social scoring by "
            "public authorities, manipulative techniques causing significant harm, untargeted "
            "scraping of facial images for recognition databases). Prohibitions apply from "
            "**2 February 2025**."
        ),
        "documents": (
            "- Legal review memo: system may not be placed on the EU market\n"
            "- Product redesign or scope change plan"
        ),
    },
}


def compose_page_content(
    *,
    industry: str,
    industry_name: str,
    use_case: str,
    use_case_name: str,
    risk_hint: str,
    citation: str,
) -> str:
    meta = _RISK_COPY.get(risk_hint, _RISK_COPY["minimal_risk"])
    tier = meta["tier_label"]

    return f"""## Quick answer

**{use_case_name}** in {industry_name.lower()} is typically classified as **{tier}** under Regulation (EU) 2024/1689 when used with EU market exposure and when it affects natural persons. Your exact tier depends on intended purpose, autonomy, and whether an Annex III exception applies.

Primary legal hook for this page: **{citation}**.

## When this use case is {tier}

{meta["legal_basis"]}

For {use_case_name.lower()} specifically: systems that evaluate, rank, filter, or monitor people in this domain often map to Annex III if they materially influence access to employment, credit, education, essential services, or similar opportunities.

## Key articles & annexes

- Regulation (EU) 2024/1689 ({citation})
- Article 6: classification rules for high-risk AI
- Article 3: definitions (provider, deployer, AI system)
- Annex III: high-risk AI systems by area of use

## Documents teams usually prepare

{meta["documents"]}

## Examples users confuse with this use case

- **Internal-only analytics** with no individual decisions → may not be high-risk, but document scope
- **Human-in-the-loop** review → does not automatically remove high-risk status if the AI still profiles or ranks people
- **Vendor vs customer role** → providers hold most conformity duties; deployers have Art. 26 obligations

## Run the questionnaire

Answer five to seven concrete questions (with examples for each) to get a rule-based classification with citations, not a generic AI opinion.

## FAQ

**Is every {use_case_name.lower()} product high-risk?**
No. Article 6(3) can exclude narrow procedural systems that do not pose significant risk, unless the system performs profiling. Document your assessment.

**Provider or deployer: who files what?**
Providers (the product vendor) typically carry Annex IV documentation and conformity duties. Deployers using a third-party tool must check Art. 26 and may need a FRIA (Art. 27) in public-sector contexts.

**When do obligations start?**
Prohibited practices: Feb 2025. GPAI rules: Aug 2025. Most Annex III high-risk rules: Aug 2026. Plan backward from your EU go-to-market date.
"""


def build_structured_data(title: str, slug: str, use_case_name: str, risk_hint: str) -> list[dict[str, Any]]:
    url = f"{settings.web_base_url}/eu-ai-act/{slug}"
    tier = _RISK_COPY.get(risk_hint, _RISK_COPY["minimal_risk"])["tier_label"]
    return [
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": f"Is {use_case_name} high-risk under the EU AI Act?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": (
                            f"{use_case_name} is often {tier} when it affects people in the EU, "
                            f"but classification depends on purpose, Annex III mapping, and "
                            f"Article 6(3) exceptions. Use the questionnaire for a cited result."
                        ),
                    },
                }
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "EU AI Act", "item": f"{settings.web_base_url}/eu-ai-act"},
                {"@type": "ListItem", "position": 2, "name": title, "item": url},
            ],
        },
    ]


async def upsert_seo_page(
    session: AsyncSession,
    *,
    slug: str,
    page_type: str,
    title: str,
    meta_description: str,
    content_md: str,
    rule_version: int,
    legal_reference_id: int | None = None,
    use_case_name: str = "",
    risk_hint: str = "minimal_risk",
) -> SEOPage:
    canonical = f"{settings.web_base_url}/eu-ai-act/{slug}"
    structured = build_structured_data(title, slug, use_case_name or title, risk_hint)
    existing = await session.execute(select(SEOPage).where(SEOPage.slug == slug))
    page = existing.scalar_one_or_none()
    now = datetime.now(timezone.utc)

    if page:
        page.title = title
        page.meta_description = meta_description
        page.content_md = content_md
        page.structured_data_json = structured
        page.last_reviewed_at = now
        page.rule_version = rule_version
        page.status = "active"
    else:
        page = SEOPage(
            slug=slug,
            page_type=page_type,
            title=title,
            meta_description=meta_description,
            content_md=content_md,
            structured_data_json=structured,
            canonical_url=canonical,
            last_reviewed_at=now,
            rule_version=rule_version,
            status="active",
        )
        session.add(page)
        await session.flush()

    if legal_reference_id:
        ref_exists = await session.execute(
            select(SEOPageReference).where(
                SEOPageReference.seo_page_id == page.id,
                SEOPageReference.legal_reference_id == legal_reference_id,
            )
        )
        if not ref_exists.scalar_one_or_none():
            session.add(
                SEOPageReference(seo_page_id=page.id, legal_reference_id=legal_reference_id)
            )

    return page


async def list_active_slugs(session: AsyncSession) -> list[str]:
    result = await session.execute(select(SEOPage.slug).where(SEOPage.status == "active"))
    return [row[0] for row in result.all()]
