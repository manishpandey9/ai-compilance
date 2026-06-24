"""pSEO page composition from structured catalog data."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import SEOPage, SEOPageReference

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


_TEMPLATE_COPY: dict[str, dict[str, str]] = {
    "annex-iv-technical-documentation": {
        "hook": "Article 11 and Annex IV",
        "answer": (
            "Annex IV technical documentation is the core evidence file providers prepare for "
            "high-risk AI systems before EU market placement. It should explain the system's "
            "intended purpose, design, data, risk controls, validation, monitoring, and human "
            "oversight in a way a reviewer can trace back to the regulation."
        ),
        "sections": (
            "- Intended purpose, provider details, and system version\n"
            "- Model, data, training, validation, and testing description\n"
            "- Risk management and post-market monitoring links\n"
            "- Human oversight, accuracy, robustness, cybersecurity, and logging controls\n"
            "- Instructions for use and conformity assessment evidence"
        ),
    },
    "fundamental-rights-impact-assessment": {
        "hook": "Article 27",
        "answer": (
            "A fundamental rights impact assessment is a deployer-side document for covered "
            "high-risk AI uses. It records the deployer's context, affected groups, foreseeable "
            "rights impacts, mitigation steps, oversight, and monitoring before deployment."
        ),
        "sections": (
            "- Deployer context and intended use\n"
            "- Affected persons and groups\n"
            "- Foreseeable impact on fundamental rights\n"
            "- Human oversight and escalation measures\n"
            "- Monitoring, complaint, and review process"
        ),
    },
    "human-oversight-plan": {
        "hook": "Article 14",
        "answer": (
            "A human oversight plan describes how people can understand, monitor, intervene in, "
            "or stop a high-risk AI system. It should be practical enough for operators, not just "
            "a policy statement."
        ),
        "sections": (
            "- Human reviewer role and authority\n"
            "- Alerts, thresholds, and escalation paths\n"
            "- Override, stop, or fallback procedure\n"
            "- Training and competency requirements\n"
            "- Monitoring records and periodic review"
        ),
    },
}


_ROLE_COPY: dict[str, dict[str, str]] = {
    "provider-vs-deployer-hr": {
        "hook": "Article 16 / Article 26",
        "answer": (
            "For HR AI, the vendor building or placing the system on the EU market is usually the "
            "provider, while the employer using it in recruitment or workforce decisions is usually "
            "the deployer. Both sides need evidence, but the provider and deployer obligations are "
            "not the same."
        ),
        "provider": (
            "- Maintain technical documentation and conformity evidence\n"
            "- Run risk management, testing, logging, and post-market monitoring\n"
            "- Provide instructions for use to deployers\n"
            "- Register where required before EU market placement"
        ),
        "deployer": (
            "- Use the system according to instructions\n"
            "- Assign trained human oversight\n"
            "- Monitor operation and keep logs where under their control\n"
            "- Complete FRIA duties when Article 27 applies"
        ),
    }
}


def _compose_template_page(*, use_case: str, use_case_name: str, citation: str) -> str | None:
    template = _TEMPLATE_COPY.get(use_case)
    if not template:
        return None
    return f"""## Quick answer

**{use_case_name}** helps teams prepare source-cited evidence for high-risk AI systems under the EU AI Act. It is not a final legal opinion or notified-body approval.

Primary legal hook for this page: **{citation}** ({template["hook"]}).

## What this template is for

{template["answer"]}

## Sections to prepare

{template["sections"]}

## What to collect before drafting

- System name, version, intended purpose, and EU market role
- Risk classification result and triggered legal references
- Data categories, affected persons, and user/deployer context
- Existing product documentation, logs, monitoring, and incident process

## Common gaps

- Treating a template as proof of compliance without product-specific evidence
- Missing the Article or Annex citation for each obligation
- Not separating provider duties from deployer duties
- Leaving human oversight or monitoring owners unnamed

## Run the questionnaire

Start with the rule-based classification. The document pack uses that result to prepare editable drafts with citations.

## FAQ

**Can a template make a system compliant by itself?**
No. It is a structured starting point. You still need product-specific evidence, review, and where applicable conformity assessment.

**Does every AI system need this template?**
No. These documents are mainly relevant when a system is high-risk or when a buyer, auditor, or counsel asks for evidence.
"""


def _compose_role_page(*, use_case: str, use_case_name: str, citation: str) -> str | None:
    role = _ROLE_COPY.get(use_case)
    if not role:
        return None
    return f"""## Quick answer

**{use_case_name}** matters because EU AI Act evidence is split by role. A provider and deployer may look at the same HR AI system but have different duties.

Primary legal hook for this page: **{citation}** ({role["hook"]}).

## Provider vs deployer

{role["answer"]}

## Provider evidence to prepare

{role["provider"]}

## Deployer evidence to prepare

{role["deployer"]}

## Common contract questions

- Which party controls model updates and instructions for use?
- Who monitors post-market performance and incidents?
- Who keeps logs and can access them?
- Who completes a FRIA if the deployment context triggers Article 27?

## Run the questionnaire

Use the questionnaire to classify the use case, identify the likely primary role, and generate source-cited evidence-prep drafts.

## FAQ

**Can a company be both provider and deployer?**
Yes. A company can carry both sets of obligations when it develops or substantially modifies a system and also uses it.

**Does using a third-party HR AI tool remove deployer duties?**
No. Deployer duties can still apply, especially around use according to instructions, human oversight, monitoring, and FRIA where required.
"""


def compose_page_content(
    *,
    industry: str,
    industry_name: str,
    use_case: str,
    use_case_name: str,
    risk_hint: str,
    citation: str,
) -> str:
    template_page = _compose_template_page(
        use_case=use_case,
        use_case_name=use_case_name,
        citation=citation,
    )
    if template_page:
        return template_page

    role_page = _compose_role_page(
        use_case=use_case,
        use_case_name=use_case_name,
        citation=citation,
    )
    if role_page:
        return role_page

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
        {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": "AI Act Navigator",
            "applicationCategory": "BusinessApplication",
            "operatingSystem": "Web",
            "url": settings.web_base_url,
            "description": (
                "Rule-based EU AI Act risk classification and evidence-prep drafts with legal "
                "article references."
            ),
            "offers": {
                "@type": "Offer",
                "price": "20",
                "priceCurrency": "USD",
            },
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
    legal_reference_ids: list[int] | None = None,
    use_case_name: str = "",
    risk_hint: str = "minimal_risk",
) -> SEOPage:
    canonical = f"{settings.web_base_url}/eu-ai-act/{slug}"
    structured = build_structured_data(title, slug, use_case_name or title, risk_hint)
    existing = await session.execute(select(SEOPage).where(SEOPage.slug == slug))
    page = existing.scalar_one_or_none()
    now = datetime.now(UTC)

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

    reference_ids = set(legal_reference_ids or [])
    if legal_reference_id:
        reference_ids.add(legal_reference_id)

    if reference_ids:
        await session.execute(
            delete(SEOPageReference).where(
                SEOPageReference.seo_page_id == page.id,
                SEOPageReference.legal_reference_id.not_in(reference_ids),
            )
        )

    for ref_id in reference_ids:
        ref_exists = await session.execute(
            select(SEOPageReference).where(
                SEOPageReference.seo_page_id == page.id,
                SEOPageReference.legal_reference_id == ref_id,
            )
        )
        if not ref_exists.scalar_one_or_none():
            session.add(SEOPageReference(seo_page_id=page.id, legal_reference_id=ref_id))

    return page


async def list_active_slugs(session: AsyncSession) -> list[str]:
    result = await session.execute(select(SEOPage.slug).where(SEOPage.status == "active"))
    return [row[0] for row in result.all()]
