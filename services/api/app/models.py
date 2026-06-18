"""ORM models only — no business logic."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    SmallInteger,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import CITEXT, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class LegalSource(Base):
    __tablename__ = "legal_source"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(Text, nullable=False)
    jurisdiction: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str | None] = mapped_column(Text)
    publication_date: Mapped[date | None] = mapped_column(Date)
    effective_date: Mapped[date | None] = mapped_column(Date)
    retrieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    version_label: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="draft")
    supersedes_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("legal_source.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    references: Mapped[list[LegalReference]] = relationship(back_populates="legal_source")


class LegalReference(Base):
    __tablename__ = "legal_reference"
    __table_args__ = (UniqueConstraint("legal_source_id", "canonical_citation"),)

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    legal_source_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("legal_source.id"), nullable=False)
    article_number: Mapped[str | None] = mapped_column(Text)
    annex_number: Mapped[str | None] = mapped_column(Text)
    section_label: Mapped[str | None] = mapped_column(Text)
    reference_text_summary: Mapped[str | None] = mapped_column(Text)
    canonical_citation: Mapped[str] = mapped_column(Text, nullable=False)
    url_fragment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    legal_source: Mapped[LegalSource] = relationship(back_populates="references")


class ActorRole(Base):
    __tablename__ = "actor_role"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class RiskTier(Base):
    __tablename__ = "risk_tier"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    severity_order: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)


class IndustryDomain(Base):
    __tablename__ = "industry_domain"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class AIUseCase(Base):
    __tablename__ = "ai_use_case"
    __table_args__ = (UniqueConstraint("industry_domain_id", "slug"),)

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    industry_domain_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("industry_domain.id"), nullable=False)
    slug: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    example_systems: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    default_risk_tier_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("risk_tier.id"))
    is_annex_iii_candidate: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class RuleSet(Base):
    __tablename__ = "rule_set"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    version: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="draft")
    legal_source_version: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RiskRule(Base):
    __tablename__ = "risk_rule"
    __table_args__ = (UniqueConstraint("rule_set_id", "rule_code"),)

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    rule_set_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("rule_set.id"), nullable=False)
    rule_code: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[int] = mapped_column(Integer, nullable=False)
    phase: Mapped[str] = mapped_column(Text, nullable=False, default="high_risk_annex_iii")
    risk_tier_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("risk_tier.id"), nullable=False)
    condition_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    legal_reference_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("legal_reference.id"), nullable=False)
    effective_from: Mapped[date | None] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class DocumentType(Base):
    __tablename__ = "document_type"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    output_formats: Mapped[list[str] | None] = mapped_column(JSONB)


class Obligation(Base):
    __tablename__ = "obligation"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    actor_role_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("actor_role.id"), nullable=False)
    risk_tier_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("risk_tier.id"), nullable=False)
    legal_reference_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("legal_reference.id"), nullable=False)
    mandatory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    evidence_required: Mapped[str | None] = mapped_column(Text)
    document_type_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("document_type.id"))
    deadline_logic: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    applicability_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    public_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    auth_provider_id: Mapped[str | None] = mapped_column(Text, unique=True)
    email: Mapped[str] = mapped_column(CITEXT, unique=True, nullable=False)
    company_name: Mapped[str | None] = mapped_column(Text)
    role: Mapped[str] = mapped_column(Text, nullable=False, default="user")
    marketing_consent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Assessment(Base):
    __tablename__ = "assessment"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    public_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    claim_token: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user.id"))
    company_name: Mapped[str | None] = mapped_column(Text)
    system_name: Mapped[str | None] = mapped_column(Text)
    email: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="draft")
    rule_version: Mapped[int | None] = mapped_column(Integer)
    source_version: Mapped[str | None] = mapped_column(Text)
    question_set_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    answers: Mapped[list[AssessmentAnswer]] = relationship(back_populates="assessment", cascade="all, delete-orphan")
    classification: Mapped[ClassificationResult | None] = relationship(
        back_populates="assessment", uselist=False, cascade="all, delete-orphan"
    )


class AssessmentAnswer(Base):
    __tablename__ = "assessment_answer"
    __table_args__ = (UniqueConstraint("assessment_id", "question_key"),)

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    assessment_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("assessment.id"), nullable=False)
    question_key: Mapped[str] = mapped_column(Text, nullable=False)
    answer_value_json: Mapped[Any] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    assessment: Mapped[Assessment] = relationship(back_populates="answers")


class ClassificationResult(Base):
    __tablename__ = "classification_result"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    assessment_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("assessment.id"), unique=True, nullable=False)
    classification_status: Mapped[str] = mapped_column(Text, nullable=False)
    risk_tier_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("risk_tier.id"))
    actor_role_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("actor_role.id"))
    confidence: Mapped[str | None] = mapped_column(Text)
    result_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    rule_version: Mapped[int] = mapped_column(Integer, nullable=False)
    source_version: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    assessment: Mapped[Assessment] = relationship(back_populates="classification")


class DocumentTemplate(Base):
    __tablename__ = "document_template"
    __table_args__ = (UniqueConstraint("document_type_id", "template_name", "version"),)

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    document_type_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("document_type.id"), nullable=False)
    template_name: Mapped[str] = mapped_column(Text, nullable=False)
    template_body: Mapped[str] = mapped_column(Text, nullable=False)
    variables_schema_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ReportJob(Base):
    __tablename__ = "report_job"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    report_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    assessment_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("assessment.id"), nullable=False)
    sku: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="queued")
    error_message: Mapped[str | None] = mapped_column(Text)
    rule_version: Mapped[int | None] = mapped_column(Integer)
    source_version: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class GeneratedDocument(Base):
    __tablename__ = "generated_document"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    assessment_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("assessment.id"), nullable=False)
    report_id: Mapped[str] = mapped_column(Text, nullable=False)
    document_type_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("document_type.id"))
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    format: Mapped[str] = mapped_column(Text, nullable=False)
    checksum: Mapped[str | None] = mapped_column(Text)
    rule_version: Mapped[int] = mapped_column(Integer, nullable=False)
    source_version: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DownloadToken(Base):
    __tablename__ = "download_token"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    token: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    assessment_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("assessment.id"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Entitlement(Base):
    __tablename__ = "entitlement"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user.id"))
    assessment_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("assessment.id"), nullable=False)
    sku: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")
    stripe_customer_id: Mapped[str | None] = mapped_column(Text)
    stripe_subscription_id: Mapped[str | None] = mapped_column(Text)
    stripe_checkout_session_id: Mapped[str | None] = mapped_column(Text, unique=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class StripeEvent(Base):
    __tablename__ = "stripe_event"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    stripe_event_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    payload_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SEOPageReference(Base):
    __tablename__ = "seo_page_reference"

    seo_page_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("seo_page.id"), primary_key=True)
    legal_reference_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("legal_reference.id"), primary_key=True
    )


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    actor_email: Mapped[str] = mapped_column(Text, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type: Mapped[str] = mapped_column(Text, nullable=False)
    entity_id: Mapped[str] = mapped_column(Text, nullable=False)
    details_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SEOPage(Base):
    __tablename__ = "seo_page"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    page_type: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    meta_description: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    content_md: Mapped[str] = mapped_column(Text, nullable=False)
    structured_data_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    canonical_url: Mapped[str] = mapped_column(Text, nullable=False)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rule_version: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

