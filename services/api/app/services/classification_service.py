"""Classification orchestration — loads rules from DB, calls pure engine."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LegalReference, Obligation, RiskRule, RiskTier, RuleSet
from app.rules.engine import ClassificationOutput, RuleRecord, classify
from app.schemas import ClassifyResponse, FreePreview, TriggeredRuleResponse


async def get_active_ruleset(session: AsyncSession) -> tuple[RuleSet | None, list[RiskRule]]:
    result = await session.execute(
        select(RuleSet).where(RuleSet.status == "active").limit(1)
    )
    ruleset = result.scalar_one_or_none()
    if not ruleset:
        return None, []

    rules_result = await session.execute(
        select(RiskRule).where(RiskRule.rule_set_id == ruleset.id, RiskRule.status == "active")
    )
    return ruleset, list(rules_result.scalars().all())


async def load_rule_records(session: AsyncSession) -> tuple[int, str, list[RuleRecord]]:
    ruleset, rules = await get_active_ruleset(session)
    if not ruleset:
        return 0, "unknown", []

    ref_ids = {r.legal_reference_id for r in rules}
    refs_result = await session.execute(
        select(LegalReference).where(LegalReference.id.in_(ref_ids))
    )
    refs = {ref.id: ref for ref in refs_result.scalars().all()}

    tier_result = await session.execute(select(RiskTier))
    tiers = {t.id: t.slug for t in tier_result.scalars().all()}

    records: list[RuleRecord] = []
    for rule in rules:
        ref = refs.get(rule.legal_reference_id)
        records.append(
            RuleRecord(
                rule_code=rule.rule_code,
                name=rule.name,
                phase=rule.phase,
                priority=rule.priority,
                risk_tier_slug=tiers.get(rule.risk_tier_id, "needs_review"),
                condition_json=rule.condition_json,
                legal_citation=ref.canonical_citation if ref else "Unknown",
                rationale_template=rule.description or rule.name,
            )
        )

    return ruleset.version, ruleset.legal_source_version or "unknown", records


async def get_obligations_preview(
    session: AsyncSession, risk_tier_slug: str, actor_role: str
) -> tuple[list[str], list[str]]:
    tier_result = await session.execute(select(RiskTier).where(RiskTier.slug == risk_tier_slug))
    tier = tier_result.scalar_one_or_none()
    if not tier:
        return [], []

    from app.models import ActorRole

    role_result = await session.execute(select(ActorRole).where(ActorRole.slug == actor_role))
    role = role_result.scalar_one_or_none()
    if not role:
        return [], []

    obl_result = await session.execute(
        select(Obligation)
        .where(Obligation.risk_tier_id == tier.id, Obligation.actor_role_id == role.id)
        .limit(10)
    )
    obligations = list(obl_result.scalars().all())

    titles = [o.title for o in obligations[:5]]
    doc_slugs: list[str] = []
    if obligations:
        from app.models import DocumentType

        doc_ids = {o.document_type_id for o in obligations if o.document_type_id}
        if doc_ids:
            docs = await session.execute(select(DocumentType).where(DocumentType.id.in_(doc_ids)))
            doc_slugs = [d.slug for d in docs.scalars().all()]
    return titles, doc_slugs


def to_classify_response(
    assessment_id: str,
    output: ClassificationOutput,
    rule_version: int,
    source_version: str,
    free_preview: FreePreview | None = None,
) -> ClassifyResponse:
    return ClassifyResponse(
        assessment_id=assessment_id,
        classification_status=output.classification_status,
        risk_tier=output.risk_tier,
        confidence=output.confidence,
        primary_actor_role=output.primary_actor_role,
        secondary_actor_roles=output.secondary_actor_roles,
        triggered_rules=[
            TriggeredRuleResponse(rule_code=t.rule_code, source=t.source, rationale=t.rationale)
            for t in output.triggered_rules
        ],
        missing_fields=output.missing_fields,
        free_preview=free_preview,
        rule_version=rule_version,
        source_version=source_version,
    )
