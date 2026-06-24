"""Pydantic request/response schemas — API contract source of truth."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    field: str | None = None
    issue: str


class ErrorEnvelope(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    error: ErrorEnvelope


class CreateAssessmentRequest(BaseModel):
    company_name: str | None = None
    system_name: str | None = None
    email: str | None = None


class CreateAssessmentResponse(BaseModel):
    assessment_id: str
    status: str
    question_set_version: int
    claim_token: str


class QuestionOption(BaseModel):
    value: str
    label: str


class NextQuestion(BaseModel):
    question_key: str
    type: Literal["single", "multi", "boolean", "text"]
    label: str
    options: list[QuestionOption] | None = None
    help: str | None = None
    allow_unknown: bool = False
    required: bool = True


class ProgressInfo(BaseModel):
    answered: int
    remaining_estimate: int


class AssessmentResponse(BaseModel):
    assessment_id: str
    status: str
    company_name: str | None = None
    system_name: str | None = None
    answers: dict[str, Any] = Field(default_factory=dict)
    next_questions: list[NextQuestion] = Field(default_factory=list)
    progress: ProgressInfo
    question_order: list[str] = Field(default_factory=list)


class PatchAssessmentRequest(BaseModel):
    company_name: str | None = None
    system_name: str | None = None
    email: str | None = None
    marketing_consent: bool | None = None
    claim_token: str | None = None


class AnswerItem(BaseModel):
    question_key: str
    value: Any


class SubmitAnswersRequest(BaseModel):
    answers: list[AnswerItem]


class RewindRequest(BaseModel):
    question_key: str


class TriggeredRuleResponse(BaseModel):
    rule_code: str
    source: str
    rationale: str


class FreePreview(BaseModel):
    top_obligations: list[str]
    document_gap_preview: list[str]


class ClassifyResponse(BaseModel):
    assessment_id: str
    classification_status: str
    risk_tier: str | None = None
    confidence: str | None = None
    primary_actor_role: str | None = None
    secondary_actor_roles: list[str] = Field(default_factory=list)
    triggered_rules: list[TriggeredRuleResponse] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    free_preview: FreePreview | None = None
    rule_version: int
    source_version: str


class SEOPageResponse(BaseModel):
    slug: str
    page_type: str
    title: str
    meta_description: str
    content_md: str
    structured_data: list[dict[str, Any]] | None = None
    canonical_url: str
    last_reviewed_at: datetime | None = None
    rule_version: int | None = None
    index_supported: bool = True
    legal_review_status: Literal["pending_sme", "approved"] = "pending_sme"
    references: list[dict[str, str]] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
    version: str = "0.1.0"


class CheckoutSessionRequest(BaseModel):
    assessment_id: str
    sku: Literal["evidence_pack"]
    success_url: str
    cancel_url: str
    customer_email: str | None = None


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str


class GenerateDocumentRequest(BaseModel):
    assessment_id: str
    sku: Literal["evidence_pack"]


class GenerateDocumentResponse(BaseModel):
    report_id: str
    status: str


class ReportArtifact(BaseModel):
    document_type: str
    format: str
    download: str


class ReportStatusResponse(BaseModel):
    report_id: str
    status: str
    rule_version: int | None = None
    source_version: str | None = None
    artifacts: list[ReportArtifact] = Field(default_factory=list)
    warnings: list[dict[str, str]] = Field(default_factory=list)
    error: str | None = None


class RulePreviewRequest(BaseModel):
    rule_set_version: int | None = None
    fixtures: list[str] = Field(default_factory=lambda: ["resume_screening", "credit_scoring", "spam_filter"])


class RulePreviewResult(BaseModel):
    fixture: str
    expected_tier: str
    actual_tier: str | None
    pass_: bool = Field(alias="pass")

    model_config = {"populate_by_name": True}


class RulePreviewResponse(BaseModel):
    results: list[RulePreviewResult]
    all_pass: bool


class PublishRuleSetRequest(BaseModel):
    rule_set_version: int


class PublishRuleSetResponse(BaseModel):
    version: int
    status: str


class ImpactResponse(BaseModel):
    affected_seo_pages: list[str]
    affected_templates: list[str]
    affected_assessments: int


class RegenerateSEORequest(BaseModel):
    scope: str = "all"
    slugs: list[str] = Field(default_factory=list)


class RegenerateSEOResponse(BaseModel):
    queued_pages: int


class CreateLegalSourceRequest(BaseModel):
    title: str
    source_type: str
    jurisdiction: str = "EU"
    url: str | None = None
    version_label: str


class LegalSourceResponse(BaseModel):
    id: int
    title: str
    version_label: str
    status: str
