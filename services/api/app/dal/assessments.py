from __future__ import annotations

import secrets
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ulid import ULID

from app.models import Assessment, AssessmentAnswer, ClassificationResult
from app.schemas import AssessmentResponse, ProgressInfo
from app.services.assessment_service import (
    count_progress,
    get_applicable_questions,
    get_ordered_question_keys,
    keys_to_clear_after,
)
from app.rules.engine import classify
from app.services.classification_service import (
    get_obligations_preview,
    load_rule_records,
    to_classify_response,
)
from app.schemas import ClassifyResponse, FreePreview


def _public_id() -> str:
    return f"aia_{ULID()}"


def _claim_token() -> str:
    return f"tok_{secrets.token_urlsafe(24)}"


async def create_assessment(
    session: AsyncSession,
    *,
    company_name: str | None = None,
    system_name: str | None = None,
) -> Assessment:
    assessment = Assessment(
        public_id=_public_id(),
        claim_token=_claim_token(),
        company_name=company_name,
        system_name=system_name,
        status="draft",
        question_set_version=1,
    )
    session.add(assessment)
    await session.flush()
    return assessment


async def get_assessment_by_public_id(session: AsyncSession, public_id: str) -> Assessment | None:
    result = await session.execute(
        select(Assessment).where(Assessment.public_id == public_id)
    )
    return result.scalar_one_or_none()


async def get_answers_map(session: AsyncSession, assessment_id: int) -> dict[str, Any]:
    result = await session.execute(
        select(AssessmentAnswer).where(AssessmentAnswer.assessment_id == assessment_id)
    )
    return {a.question_key: a.answer_value_json for a in result.scalars().all()}


async def build_assessment_response(session: AsyncSession, assessment: Assessment) -> AssessmentResponse:
    answers = await get_answers_map(session, assessment.id)
    next_questions = get_applicable_questions(answers)
    answered, remaining = count_progress(answers)
    return AssessmentResponse(
        assessment_id=assessment.public_id,
        status=assessment.status,
        company_name=assessment.company_name,
        system_name=assessment.system_name,
        answers=answers,
        next_questions=next_questions,
        progress=ProgressInfo(answered=answered, remaining_estimate=remaining),
        question_order=get_ordered_question_keys(answers),
    )


async def upsert_answers(
    session: AsyncSession,
    assessment: Assessment,
    answers: list[tuple[str, Any]],
) -> AssessmentResponse:
    existing = await session.execute(
        select(AssessmentAnswer).where(AssessmentAnswer.assessment_id == assessment.id)
    )
    by_key = {a.question_key: a for a in existing.scalars().all()}

    for key, value in answers:
        if key in by_key:
            by_key[key].answer_value_json = value
        else:
            session.add(
                AssessmentAnswer(
                    assessment_id=assessment.id,
                    question_key=key,
                    answer_value_json=value,
                )
            )

    if assessment.status == "draft":
        assessment.status = "in_progress"
    await session.flush()
    return await build_assessment_response(session, assessment)


async def rewind_assessment(
    session: AsyncSession,
    assessment: Assessment,
    question_key: str,
) -> AssessmentResponse:
    """Remove answers from question_key onward so the user can edit that step."""
    answers = await get_answers_map(session, assessment.id)
    keys_to_clear = keys_to_clear_after(answers, question_key)
    if not keys_to_clear:
        raise ValueError(f"Unknown question key: {question_key}")

    result = await session.execute(
        select(AssessmentAnswer).where(
            AssessmentAnswer.assessment_id == assessment.id,
            AssessmentAnswer.question_key.in_(keys_to_clear),
        )
    )
    for row in result.scalars().all():
        await session.delete(row)

    if assessment.status == "completed":
        assessment.status = "in_progress"
        assessment.completed_at = None
        cr_result = await session.execute(
            select(ClassificationResult).where(ClassificationResult.assessment_id == assessment.id)
        )
        existing_cr = cr_result.scalar_one_or_none()
        if existing_cr:
            await session.delete(existing_cr)

    await session.flush()
    return await build_assessment_response(session, assessment)


async def run_classification(session: AsyncSession, assessment: Assessment) -> ClassifyResponse:
    answers = await get_answers_map(session, assessment.id)
    rule_version, source_version, rules = await load_rule_records(session)
    output = classify(answers, rules, rule_version=rule_version, source_version=source_version)

    free_preview = None
    if output.classification_status == "classified" and output.risk_tier and output.primary_actor_role:
        titles, docs = await get_obligations_preview(
            session, output.risk_tier, output.primary_actor_role
        )
        free_preview = FreePreview(top_obligations=titles, document_gap_preview=docs)

    assessment.rule_version = rule_version
    assessment.source_version = source_version
    assessment.status = "completed"
    assessment.completed_at = assessment.completed_at or __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc
    )

    from app.models import ActorRole, RiskTier

    risk_tier_id = None
    actor_role_id = None
    if output.risk_tier:
        rt = await session.execute(select(RiskTier).where(RiskTier.slug == output.risk_tier))
        tier = rt.scalar_one_or_none()
        risk_tier_id = tier.id if tier else None
    if output.primary_actor_role:
        ar = await session.execute(select(ActorRole).where(ActorRole.slug == output.primary_actor_role))
        role = ar.scalar_one_or_none()
        actor_role_id = role.id if role else None

    existing_cr = await session.execute(
        select(ClassificationResult).where(ClassificationResult.assessment_id == assessment.id)
    )
    existing = existing_cr.scalar_one_or_none()

    if existing:
        existing.classification_status = output.classification_status
        existing.risk_tier_id = risk_tier_id
        existing.actor_role_id = actor_role_id
        existing.confidence = output.confidence
        existing.result_json = output.result_json
        existing.rule_version = rule_version
        existing.source_version = source_version
    else:
        session.add(
            ClassificationResult(
                assessment_id=assessment.id,
                classification_status=output.classification_status,
                risk_tier_id=risk_tier_id,
                actor_role_id=actor_role_id,
                confidence=output.confidence,
                result_json=output.result_json,
                rule_version=rule_version,
                source_version=source_version,
            )
        )

    await session.flush()
    return to_classify_response(
        assessment.public_id, output, rule_version, source_version, free_preview
    )
