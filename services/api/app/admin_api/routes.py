from datetime import UTC

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin_api.deps import require_admin
from app.db import get_db
from app.models import Assessment, AuditLog, LegalSource, RuleSet, SEOPage
from app.schemas import (
    CreateLegalSourceRequest,
    ImpactResponse,
    LegalSourceResponse,
    PublishRuleSetRequest,
    PublishRuleSetResponse,
    RegenerateSEORequest,
    RegenerateSEOResponse,
    RulePreviewRequest,
    RulePreviewResponse,
    RulePreviewResult,
)
from app.scripts.generate_pseo import generate_pages

router = APIRouter(prefix="/admin", tags=["admin"])

FIXTURES = {
    "resume_screening": (
        "high_risk",
        {
            "eu_market_exposure": "yes",
            "actor_role": "provider",
            "use_case_category": "employment_recruitment",
            "affects_natural_persons": True,
            "system_function": ["filter_applications", "rank_candidates"],
        },
    ),
    "credit_scoring": (
        "high_risk",
        {
            "eu_market_exposure": "yes",
            "actor_role": "provider",
            "use_case_category": "credit_financial",
            "affects_natural_persons": True,
            "system_function": ["credit_scoring"],
        },
    ),
    "spam_filter": (
        "minimal_risk",
        {
            "eu_market_exposure": "yes",
            "actor_role": "provider",
            "use_case_category": "other",
            "affects_natural_persons": False,
        },
    ),
}


@router.post("/legal-sources", response_model=LegalSourceResponse)
async def create_legal_source(
    body: CreateLegalSourceRequest,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
) -> LegalSourceResponse:
    source = LegalSource(
        title=body.title,
        source_type=body.source_type,
        jurisdiction=body.jurisdiction,
        url=body.url,
        version_label=body.version_label,
        status="draft",
    )
    db.add(source)
    db.add(
        AuditLog(
            actor_email="admin",
            action="create",
            entity_type="legal_source",
            entity_id=body.title,
            details_json=body.model_dump(),
        )
    )
    await db.flush()
    return LegalSourceResponse(
        id=source.id, title=source.title, version_label=source.version_label, status=source.status
    )


@router.post("/rules/preview", response_model=RulePreviewResponse)
async def preview_rules(
    body: RulePreviewRequest,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
) -> RulePreviewResponse:
    from app.rules.engine import classify
    from app.services.classification_service import load_rule_records

    _, _, rules = await load_rule_records(db)
    results: list[RulePreviewResult] = []

    for name in body.fixtures:
        expected, facts = FIXTURES.get(name, ("minimal_risk", {}))
        output = classify(facts, rules)
        actual = output.risk_tier or output.classification_status
        results.append(
            RulePreviewResult(
                fixture=name,
                expected_tier=expected,
                actual_tier=actual,
                pass_=actual == expected,
            )
        )

    return RulePreviewResponse(results=results, all_pass=all(r.pass_ for r in results))


@router.get("/rules/impact", response_model=ImpactResponse)
async def rules_impact(
    rule_set_version: int,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
) -> ImpactResponse:
    pages = await db.execute(select(SEOPage.slug).where(SEOPage.rule_version == rule_set_version))
    slugs = [r[0] for r in pages.all()]
    count = (
        await db.execute(select(func.count()).select_from(Assessment).where(Assessment.rule_version == rule_set_version))
    ).scalar() or 0
    return ImpactResponse(
        affected_seo_pages=slugs,
        affected_templates=[s for s in slugs if s.startswith("templates/")],
        affected_assessments=count,
    )


@router.post("/rules/publish", response_model=PublishRuleSetResponse)
async def publish_rules(
    body: PublishRuleSetRequest,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
) -> PublishRuleSetResponse:
    preview = await preview_rules(RulePreviewRequest(), db, _admin)
    if not preview.all_pass:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=409,
            detail={"error": {"code": "conflict", "message": "Fixture suite failed", "details": []}},
        )

    target = (
        await db.execute(select(RuleSet).where(RuleSet.version == body.rule_set_version))
    ).scalar_one_or_none()
    if not target:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Rule set not found", "details": []}})

    active = (await db.execute(select(RuleSet).where(RuleSet.status == "active"))).scalars().all()
    for rs in active:
        rs.status = "superseded"
    target.status = "active"
    from datetime import datetime

    target.published_at = datetime.now(UTC)
    db.add(
        AuditLog(
            actor_email="admin",
            action="publish",
            entity_type="rule_set",
            entity_id=str(body.rule_set_version),
        )
    )
    await db.flush()
    return PublishRuleSetResponse(version=target.version, status=target.status)


@router.post("/seo-pages/regenerate", response_model=RegenerateSEOResponse, status_code=202)
async def regenerate_seo(
    body: RegenerateSEORequest,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
) -> RegenerateSEOResponse:
    generated_pages = await generate_pages(db)
    return RegenerateSEOResponse(queued_pages=generated_pages)
