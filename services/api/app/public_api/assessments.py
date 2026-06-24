from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dal import assessments as assessment_dal
from app.db import get_db
from app.schemas import (
    AssessmentResponse,
    ClassifyResponse,
    CreateAssessmentRequest,
    CreateAssessmentResponse,
    PatchAssessmentRequest,
    RewindRequest,
    SubmitAnswersRequest,
)

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("", response_model=CreateAssessmentResponse, status_code=201)
async def create_assessment(
    body: CreateAssessmentRequest,
    db: AsyncSession = Depends(get_db),
) -> CreateAssessmentResponse:
    assessment = await assessment_dal.create_assessment(
        db, company_name=body.company_name, system_name=body.system_name
    )
    if body.email is not None:
        assessment.email = body.email
        await db.flush()
    return CreateAssessmentResponse(
        assessment_id=assessment.public_id,
        status=assessment.status,
        question_set_version=assessment.question_set_version,
        claim_token=assessment.claim_token,
    )


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: str,
    db: AsyncSession = Depends(get_db),
) -> AssessmentResponse:
    assessment = await assessment_dal.get_assessment_by_public_id(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Assessment not found", "details": []}})
    return await assessment_dal.build_assessment_response(db, assessment)


@router.patch("/{assessment_id}", response_model=AssessmentResponse)
async def patch_assessment(
    assessment_id: str,
    body: PatchAssessmentRequest,
    db: AsyncSession = Depends(get_db),
) -> AssessmentResponse:
    assessment = await assessment_dal.get_assessment_by_public_id(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Assessment not found", "details": []}})
    if body.company_name is not None:
        assessment.company_name = body.company_name
    if body.system_name is not None:
        assessment.system_name = body.system_name
    if body.email is not None:
        assessment.email = body.email
    await db.flush()
    return await assessment_dal.build_assessment_response(db, assessment)


@router.post("/{assessment_id}/answers", response_model=AssessmentResponse)
async def submit_answers(
    assessment_id: str,
    body: SubmitAnswersRequest,
    db: AsyncSession = Depends(get_db),
) -> AssessmentResponse:
    assessment = await assessment_dal.get_assessment_by_public_id(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Assessment not found", "details": []}})
    pairs = [(a.question_key, a.value) for a in body.answers]
    return await assessment_dal.upsert_answers(db, assessment, pairs)


@router.post("/{assessment_id}/rewind", response_model=AssessmentResponse)
async def rewind_assessment(
    assessment_id: str,
    body: RewindRequest,
    db: AsyncSession = Depends(get_db),
) -> AssessmentResponse:
    assessment = await assessment_dal.get_assessment_by_public_id(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Assessment not found", "details": []}})
    try:
        return await assessment_dal.rewind_assessment(db, assessment, body.question_key)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "invalid_question", "message": str(exc), "details": []}},
        ) from exc


@router.get("/{assessment_id}/result", response_model=ClassifyResponse)
async def get_assessment_result(
    assessment_id: str,
    db: AsyncSession = Depends(get_db),
) -> ClassifyResponse:
    from app.models import ClassificationResult
    from app.schemas import FreePreview, TriggeredRuleResponse
    from app.services.classification_service import get_obligations_preview, to_classify_response
    from app.models import RiskTier, ActorRole

    assessment = await assessment_dal.get_assessment_by_public_id(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Assessment not found", "details": []}})

    cr_result = await db.execute(
        select(ClassificationResult).where(ClassificationResult.assessment_id == assessment.id)
    )
    cr = cr_result.scalar_one_or_none()
    if not cr:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Result not found", "details": []}})
    risk_slug = None
    if cr.risk_tier_id:
        tier = (await db.execute(select(RiskTier).where(RiskTier.id == cr.risk_tier_id))).scalar_one_or_none()
        risk_slug = tier.slug if tier else None
    role_slug = None
    if cr.actor_role_id:
        role = (await db.execute(select(ActorRole).where(ActorRole.id == cr.actor_role_id))).scalar_one_or_none()
        role_slug = role.slug if role else None

    from app.rules.engine import ClassificationOutput, TriggeredRule

    raw_triggered = (cr.result_json or {}).get("triggered_rules", [])
    output = ClassificationOutput(
        classification_status=cr.classification_status,
        risk_tier=risk_slug,
        confidence=cr.confidence,
        primary_actor_role=role_slug,
        secondary_actor_roles=[],
        triggered_rules=[
            TriggeredRule(
                rule_code=t.get("rule_code", ""),
                source=t.get("source", ""),
                rationale=t.get("rationale", ""),
                phase=t.get("phase", ""),
            )
            for t in raw_triggered
        ],
        missing_fields=[],
        result_json=cr.result_json,
    )
    free_preview = None
    if risk_slug and role_slug:
        titles, docs = await get_obligations_preview(db, risk_slug, role_slug)
        free_preview = FreePreview(top_obligations=titles, document_gap_preview=docs)

    return to_classify_response(
        assessment.public_id, output, cr.rule_version, cr.source_version, free_preview
    )


@router.post("/{assessment_id}/classify", response_model=ClassifyResponse)
async def classify_assessment(
    assessment_id: str,
    db: AsyncSession = Depends(get_db),
) -> ClassifyResponse:
    assessment = await assessment_dal.get_assessment_by_public_id(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Assessment not found", "details": []}})
    return await assessment_dal.run_classification(db, assessment)
