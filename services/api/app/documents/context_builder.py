"""Build document RenderContext from locked assessment snapshot."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.documents.labels import actor_role_label, answer_narrative, risk_tier_label
from app.documents.spec import ObligationRow, RenderContext, TriggeredRuleRow
from app.models import (
    ActorRole,
    Assessment,
    AssessmentAnswer,
    ClassificationResult,
    DocumentType,
    LegalReference,
    LegalSource,
    Obligation,
    RiskRule,
    RiskTier,
)


_ENFORCEMENT = {
    "prohibited": "Prohibited practices: 2 February 2025",
    "high_risk": "Annex III high-risk rules: 2 August 2026 (extensions may apply for embedded products)",
    "limited_risk": "Transparency rules: phased with GPAI and high-risk timelines",
    "minimal_risk": "No Annex III conformity deadline; monitor codes of conduct",
}


def _default_owner(actor_slug: str, title: str) -> str:
    t = title.lower()
    if "deployer" in t or actor_slug == "deployer":
        return "Customer success / legal"
    if "technical" in t or "annex iv" in t:
        return "Engineering / product"
    if "oversight" in t or "human" in t:
        return "Operations / HR"
    if "risk" in t:
        return "Compliance / legal"
    if "logging" in t or "record" in t:
        return "Engineering / security"
    return "Compliance owner"


def load_answers(session: Session, assessment_id: int) -> dict[str, Any]:
    rows = session.execute(
        select(AssessmentAnswer).where(AssessmentAnswer.assessment_id == assessment_id)
    ).scalars()
    return {a.question_key: a.answer_value_json for a in rows}


def build_render_context(
    session: Session,
    *,
    assessment: Assessment,
    classification: ClassificationResult,
    pack_sku: str,
) -> RenderContext:
    answers = load_answers(session, assessment.id)
    result_json = classification.result_json or {}
    triggered_raw = result_json.get("triggered_rules", [])

    tier_slug = "minimal_risk"
    tier_label = risk_tier_label(tier_slug)
    if classification.risk_tier_id:
        tier = session.get(RiskTier, classification.risk_tier_id)
        if tier:
            tier_slug = tier.slug
            tier_label = tier.name if tier.name else risk_tier_label(tier.slug)

    actor_slug = "provider"
    actor_label = actor_role_label(actor_slug)
    if classification.actor_role_id:
        role = session.get(ActorRole, classification.actor_role_id)
        if role:
            actor_slug = role.slug
            actor_label = role.name

    # Enrich triggered rules with DB legal references
    rule_codes = [t.get("rule_code") for t in triggered_raw if t.get("rule_code")]
    rules_by_code: dict[str, RiskRule] = {}
    if rule_codes:
        rules = session.execute(
            select(RiskRule).where(RiskRule.rule_code.in_(rule_codes))
        ).scalars()
        rules_by_code = {r.rule_code: r for r in rules}

    ref_ids = {r.legal_reference_id for r in rules_by_code.values()}
    refs: dict[int, LegalReference] = {}
    sources: dict[int, LegalSource] = {}
    if ref_ids:
        ref_rows = session.execute(
            select(LegalReference).where(LegalReference.id.in_(ref_ids))
        ).scalars()
        refs = {r.id: r for r in ref_rows}
        source_ids = {r.legal_source_id for r in refs.values()}
        if source_ids:
            src_rows = session.execute(
                select(LegalSource).where(LegalSource.id.in_(source_ids))
            ).scalars()
            sources = {s.id: s for s in src_rows}

    triggered_rules: list[TriggeredRuleRow] = []
    for raw in triggered_raw:
        code = raw.get("rule_code", "")
        db_rule = rules_by_code.get(code)
        citation = raw.get("source", "Unknown")
        summary = ""
        url = None
        name = code
        if db_rule:
            name = db_rule.name
            ref = refs.get(db_rule.legal_reference_id)
            if ref:
                citation = ref.canonical_citation
                summary = ref.reference_text_summary or ""
                src = sources.get(ref.legal_source_id)
                if src:
                    url = src.url
        triggered_rules.append(
            TriggeredRuleRow(
                rule_code=code,
                name=name,
                legal_citation=citation,
                legal_summary=summary,
                rationale=raw.get("rationale", ""),
                source_url=url,
            )
        )

    obligations: list[ObligationRow] = []
    required_docs: list[str] = []
    if classification.risk_tier_id and classification.actor_role_id:
        obl_list = list(
            session.execute(
                select(Obligation)
                .where(
                    Obligation.risk_tier_id == classification.risk_tier_id,
                    Obligation.actor_role_id == classification.actor_role_id,
                )
                .order_by(Obligation.id)
            ).scalars()
        )

        obl_ref_ids = {o.legal_reference_id for o in obl_list}
        obl_refs = {}
        if obl_ref_ids:
            for ref in session.execute(
                select(LegalReference).where(LegalReference.id.in_(obl_ref_ids))
            ).scalars():
                obl_refs[ref.id] = ref

        doc_type_ids = {o.document_type_id for o in obl_list if o.document_type_id}
        doc_types: dict[int, DocumentType] = {}
        if doc_type_ids:
            for dt in session.execute(
                select(DocumentType).where(DocumentType.id.in_(doc_type_ids))
            ).scalars():
                doc_types[dt.id] = dt

        for i, obl in enumerate(obl_list, start=1):
            ref = obl_refs.get(obl.legal_reference_id)
            if not ref:
                raise ValueError(f"Obligation '{obl.title}' has no legal reference")
            src = sources.get(ref.legal_source_id) or session.get(LegalSource, ref.legal_source_id)
            doc_slug = None
            if obl.document_type_id and obl.document_type_id in doc_types:
                doc_slug = doc_types[obl.document_type_id].slug
                if doc_slug not in required_docs:
                    required_docs.append(doc_slug)

            deadline = _ENFORCEMENT.get(tier_slug)
            obligations.append(
                ObligationRow(
                    obligation_id=f"OBL-{i:03d}",
                    title=obl.title,
                    description=obl.description,
                    legal_citation=ref.canonical_citation,
                    legal_summary=ref.reference_text_summary,
                    source_url=src.url if src else None,
                    mandatory=obl.mandatory,
                    evidence_required=obl.evidence_required,
                    document_type=doc_slug,
                    suggested_owner=_default_owner(actor_slug, obl.title),
                    enforcement_note=deadline,
                )
            )

    missing: list[str] = []
    if not assessment.company_name:
        missing.append("company_name")
    if not assessment.system_name:
        missing.append("system_name")
    if not answers.get("use_case_category"):
        missing.append("use_case_category")

    primary_source = session.execute(
        select(LegalSource).where(LegalSource.status == "active").limit(1)
    ).scalar_one_or_none()

    ctx = RenderContext(
        assessment_id=assessment.public_id,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        company_name=assessment.company_name or "[Company name not provided]",
        system_name=assessment.system_name or "[System name not provided]",
        risk_tier=tier_slug,
        risk_tier_label=tier_label,
        primary_actor_role=actor_slug,
        actor_role_label=actor_label,
        classification_status=classification.classification_status,
        confidence=classification.confidence,
        rule_version=classification.rule_version,
        source_version=classification.source_version,
        legal_source_title=primary_source.title if primary_source else "Regulation (EU) 2024/1689",
        legal_source_url=primary_source.url if primary_source and primary_source.url else "",
        triggered_rules=triggered_rules,
        obligations=obligations,
        answers=answers,
        answer_rows=answer_narrative(answers),
        missing_variables=missing,
        pack_sku=pack_sku,
        required_documents=required_docs,
        is_high_risk=tier_slug == "high_risk",
        needs_fria=tier_slug == "high_risk" and actor_slug == "deployer",
        needs_provider_conformity=tier_slug == "high_risk" and actor_slug == "provider",
    )
    ctx.validate()
    return ctx
