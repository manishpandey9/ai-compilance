"""Upsert production-grade legal references and obligations (idempotent)."""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import ActorRole, DocumentType, LegalReference, LegalSource, Obligation, RiskTier

CIT = "Regulation (EU) 2024/1689"

# Legacy obligations with wrong article mappings (e.g. Art. 9 duty cited to Annex III).
LEGACY_OBLIGATION_TITLES = [
    "Establish risk management system",
    "Prepare technical documentation (Annex IV)",
]

# Near-duplicate titles superseded by EUR-Lex-aligned obligation names.
SUPERSEDED_OBLIGATION_TITLES = [
    "Maintain logging and record-keeping",
    "Provide instructions and transparency to deployers",
    "Enable human oversight",
    "Comply with provider obligations (Art. 16)",
    "Register in EU database",
]


def _ref(
    source_id: int,
    *,
    citation: str,
    article: str | None = None,
    annex: str | None = None,
    section: str | None = None,
    summary: str,
) -> LegalReference:
    return LegalReference(
        legal_source_id=source_id,
        article_number=article,
        annex_number=annex,
        section_label=section,
        canonical_citation=citation,
        reference_text_summary=summary,
    )


def _ensure_refs(session: Session, source_id: int) -> dict[str, LegalReference]:
    existing = {
        r.canonical_citation: r
        for r in session.execute(
            select(LegalReference).where(LegalReference.legal_source_id == source_id)
        ).scalars()
    }
    specs = [
        ("annex_iii_4a", f"{CIT} Annex III point 4(a)", None, "III", "point 4(a)", "AI for recruitment or selection"),
        ("annex_iii_5b", f"{CIT} Annex III point 5(b)", None, "III", "point 5(b)", "AI for creditworthiness evaluation"),
        ("art_9", f"{CIT} Article 9", "9", None, None, "Risk management system"),
        ("art_10", f"{CIT} Article 10", "10", None, None, "Data and data governance"),
        ("art_11", f"{CIT} Article 11", "11", None, None, "Technical documentation"),
        ("annex_iv", f"{CIT} Annex IV", None, "IV", None, "Technical documentation content"),
        ("art_12", f"{CIT} Article 12", "12", None, None, "Record-keeping and logging"),
        ("art_13", f"{CIT} Article 13", "13", None, None, "Transparency and information for deployers"),
        ("art_14", f"{CIT} Article 14", "14", None, None, "Human oversight"),
        ("art_15", f"{CIT} Article 15", "15", None, None, "Accuracy, robustness and cybersecurity"),
        ("art_16", f"{CIT} Article 16", "16", None, None, "Provider obligations for high-risk AI"),
        ("art_17", f"{CIT} Article 17", "17", None, None, "Quality management system"),
        ("art_18", f"{CIT} Article 18", "18", None, None, "Documentation retention"),
        ("art_26", f"{CIT} Article 26", "26", None, None, "Deployer obligations"),
        ("art_27", f"{CIT} Article 27", "27", None, None, "Fundamental rights impact assessment"),
        ("art_43", f"{CIT} Article 43", "43", None, None, "Conformity assessment"),
        ("art_47", f"{CIT} Article 47", "47", None, None, "EU declaration of conformity"),
        ("art_49", f"{CIT} Article 49", "49", None, None, "EU database registration"),
        ("art_50", f"{CIT} Article 50", "50", None, None, "Transparency obligations"),
        ("art_72", f"{CIT} Article 72", "72", None, None, "Post-market monitoring"),
        ("art_73", f"{CIT} Article 73", "73", None, None, "Serious incident reporting"),
    ]
    for key, citation, article, annex, section, summary in specs:
        if citation not in existing:
            ref = _ref(
                source_id,
                citation=citation,
                article=article,
                annex=annex,
                section=section,
                summary=summary,
            )
            session.add(ref)
            existing[citation] = ref
    session.flush()
    by_key = {}
    for key, citation, *_ in specs:
        by_key[key] = existing[citation]
    return by_key


def _ensure_doc_types(session: Session) -> dict[str, DocumentType]:
    specs = [
        ("risk_classification_memo", "Risk Classification Memo", ["pdf", "md"]),
        ("annex-iv-technical-documentation", "Annex IV Technical Documentation", ["docx"]),
        ("quality-management-system", "Quality Management System", ["docx"]),
        ("human-oversight-plan", "Human Oversight Plan", ["docx"]),
        ("instructions-for-use", "Instructions for Use", ["docx"]),
        ("fria-template", "Fundamental Rights Impact Assessment", ["docx"]),
        ("eu-declaration-of-conformity", "EU Declaration of Conformity", ["docx"]),
        ("eu-database-registration", "EU Database Registration Pack", ["csv"]),
        ("evidence-tracker", "Evidence Tracker", ["xlsx"]),
    ]
    existing = {d.slug: d for d in session.execute(select(DocumentType)).scalars()}
    for slug, name, formats in specs:
        if slug not in existing:
            dt = DocumentType(slug=slug, name=name, output_formats=formats)
            session.add(dt)
            existing[slug] = dt
    session.flush()
    return existing


def _cleanup_legacy(session: Session) -> None:
    for title in [*LEGACY_OBLIGATION_TITLES, *SUPERSEDED_OBLIGATION_TITLES]:
        session.execute(delete(Obligation).where(Obligation.title == title))


def upsert_production_obligations(session: Session) -> None:
    """Ensure EUR-Lex-aligned refs, document types, and obligations exist."""
    source = session.execute(
        select(LegalSource).where(LegalSource.status == "active").limit(1)
    ).scalar_one_or_none()
    if not source:
        return

    _cleanup_legacy(session)
    refs = _ensure_refs(session, source.id)
    docs = _ensure_doc_types(session)

    provider = session.execute(select(ActorRole).where(ActorRole.slug == "provider")).scalar_one()
    deployer = session.execute(select(ActorRole).where(ActorRole.slug == "deployer")).scalar_one()
    high = session.execute(select(RiskTier).where(RiskTier.slug == "high_risk")).scalar_one()
    limited = session.execute(select(RiskTier).where(RiskTier.slug == "limited_risk")).scalar_one()

    existing_titles = {o.title for o in session.execute(select(Obligation)).scalars()}

    def add(**kwargs: object) -> None:
        title = str(kwargs["title"])
        if title in existing_titles:
            return
        session.add(Obligation(**kwargs))  # type: ignore[arg-type]
        existing_titles.add(title)

    # High-risk provider obligations (Chapter III Section 2)
    provider_high = [
        (
            "Establish and maintain risk management system",
            refs["art_9"],
            "Risk management policy, hazard analysis, mitigation and review log",
            docs["risk_classification_memo"].id,
        ),
        (
            "Implement data and data governance practices",
            refs["art_10"],
            "Dataset documentation, bias testing, lineage and quality criteria",
            None,
        ),
        (
            "Draw up technical documentation per Annex IV",
            refs["art_11"],
            "Completed Annex IV package per Article 11",
            docs["annex-iv-technical-documentation"].id,
        ),
        (
            "Maintain automatic logging and record-keeping",
            refs["art_12"],
            "Logging architecture, retention policy, sample logs",
            None,
        ),
        (
            "Supply instructions for use to deployers",
            refs["art_13"],
            "Instructions for use document and deployer information pack",
            docs["instructions-for-use"].id,
        ),
        (
            "Design for effective human oversight",
            refs["art_14"],
            "Human oversight plan and deployer oversight measures",
            docs["human-oversight-plan"].id,
        ),
        (
            "Ensure accuracy, robustness and cybersecurity",
            refs["art_15"],
            "Test reports, security assessment, performance benchmarks",
            None,
        ),
        (
            "Comply with provider obligations under Article 16",
            refs["art_16"],
            "Provider compliance checklist and management review",
            None,
        ),
        (
            "Maintain quality management system",
            refs["art_17"],
            "Written QMS policies and procedures per Article 17(1)",
            docs["quality-management-system"].id,
        ),
        (
            "Retain documentation for 10 years",
            refs["art_18"],
            "Archive of technical documentation and QMS records",
            None,
        ),
        (
            "Establish post-market monitoring system",
            refs["art_72"],
            "Post-market monitoring plan per Article 72(3)",
            None,
        ),
        (
            "Report serious incidents",
            refs["art_73"],
            "Serious incident reporting procedure and contact paths",
            None,
        ),
        (
            "Complete conformity assessment where required",
            refs["art_43"],
            "Conformity assessment report; notified body certificate if applicable",
            None,
        ),
        (
            "Issue EU declaration of conformity",
            refs["art_47"],
            "Signed EU declaration per Annex V",
            docs["eu-declaration-of-conformity"].id,
        ),
        (
            "Register high-risk system in EU database",
            refs["art_49"],
            "EU database registration confirmation per Annex VIII",
            docs["eu-database-registration"].id,
        ),
    ]
    for title, ref, evidence, doc_id in provider_high:
        add(
            title=title,
            actor_role_id=provider.id,
            risk_tier_id=high.id,
            legal_reference_id=ref.id,
            evidence_required=evidence,
            document_type_id=doc_id,
        )

    add(
        title="Inform users of AI interaction",
        actor_role_id=provider.id,
        risk_tier_id=limited.id,
        legal_reference_id=refs["art_50"].id,
        evidence_required="UI disclosure copy and interaction design documentation",
    )
    add(
        title="Label AI-generated or manipulated content",
        actor_role_id=provider.id,
        risk_tier_id=limited.id,
        legal_reference_id=refs["art_50"].id,
        evidence_required="Content labeling policy and implementation evidence",
    )

    add(
        title="Use high-risk AI per provider instructions",
        description="Deployers must use the system according to instructions for use.",
        actor_role_id=deployer.id,
        risk_tier_id=high.id,
        legal_reference_id=refs["art_26"].id,
        evidence_required="Signed acceptance of instructions; deployment SOP",
    )
    add(
        title="Perform fundamental rights impact assessment (FRIA)",
        description="Required for certain public-sector and specified deployers before deployment.",
        actor_role_id=deployer.id,
        risk_tier_id=high.id,
        legal_reference_id=refs["art_27"].id,
        evidence_required="Completed FRIA and market surveillance notification where required",
        document_type_id=docs["fria-template"].id,
    )

    session.flush()
