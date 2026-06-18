"""Initial schema."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")

    op.create_table(
        "legal_source",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("source_type", sa.Text(), nullable=False),
        sa.Column("jurisdiction", sa.Text(), nullable=False),
        sa.Column("url", sa.Text()),
        sa.Column("publication_date", sa.Date()),
        sa.Column("effective_date", sa.Date()),
        sa.Column("retrieved_at", sa.DateTime(timezone=True)),
        sa.Column("version_label", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="draft"),
        sa.Column("supersedes_id", sa.BigInteger(), sa.ForeignKey("legal_source.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("title", "version_label"),
    )

    op.create_table(
        "legal_reference",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("legal_source_id", sa.BigInteger(), sa.ForeignKey("legal_source.id"), nullable=False),
        sa.Column("article_number", sa.Text()),
        sa.Column("annex_number", sa.Text()),
        sa.Column("section_label", sa.Text()),
        sa.Column("reference_text_summary", sa.Text()),
        sa.Column("canonical_citation", sa.Text(), nullable=False),
        sa.Column("url_fragment", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("legal_source_id", "canonical_citation"),
    )

    op.create_table(
        "actor_role",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("slug", sa.Text(), unique=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text()),
    )

    op.create_table(
        "risk_tier",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("slug", sa.Text(), unique=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("severity_order", sa.SmallInteger(), nullable=False, server_default="0"),
    )

    op.create_table(
        "industry_domain",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("slug", sa.Text(), unique=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text()),
    )

    op.create_table(
        "ai_use_case",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("industry_domain_id", sa.BigInteger(), sa.ForeignKey("industry_domain.id"), nullable=False),
        sa.Column("slug", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("example_systems", postgresql.JSONB()),
        sa.Column("default_risk_tier_id", sa.BigInteger(), sa.ForeignKey("risk_tier.id")),
        sa.Column("is_annex_iii_candidate", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("industry_domain_id", "slug"),
    )

    op.create_table(
        "rule_set",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("version", sa.Integer(), unique=True, nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="draft"),
        sa.Column("legal_source_version", sa.Text()),
        sa.Column("notes", sa.Text()),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index(
        "ix_one_active_ruleset",
        "rule_set",
        ["status"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )

    op.create_table(
        "document_type",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("slug", sa.Text(), unique=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("output_formats", postgresql.JSONB()),
    )

    op.create_table(
        "risk_rule",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("rule_set_id", sa.BigInteger(), sa.ForeignKey("rule_set.id"), nullable=False),
        sa.Column("rule_code", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("phase", sa.Text(), nullable=False, server_default="high_risk_annex_iii"),
        sa.Column("risk_tier_id", sa.BigInteger(), sa.ForeignKey("risk_tier.id"), nullable=False),
        sa.Column("condition_json", postgresql.JSONB(), nullable=False),
        sa.Column("legal_reference_id", sa.BigInteger(), sa.ForeignKey("legal_reference.id"), nullable=False),
        sa.Column("effective_from", sa.Date()),
        sa.Column("effective_to", sa.Date()),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("rule_set_id", "rule_code"),
    )

    op.create_table(
        "obligation",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("actor_role_id", sa.BigInteger(), sa.ForeignKey("actor_role.id"), nullable=False),
        sa.Column("risk_tier_id", sa.BigInteger(), sa.ForeignKey("risk_tier.id"), nullable=False),
        sa.Column("legal_reference_id", sa.BigInteger(), sa.ForeignKey("legal_reference.id"), nullable=False),
        sa.Column("mandatory", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("evidence_required", sa.Text()),
        sa.Column("document_type_id", sa.BigInteger(), sa.ForeignKey("document_type.id")),
        sa.Column("deadline_logic", postgresql.JSONB()),
        sa.Column("applicability_json", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "user",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("public_id", sa.Text(), unique=True, nullable=False),
        sa.Column("auth_provider_id", sa.Text(), unique=True),
        sa.Column("email", postgresql.CITEXT(), unique=True, nullable=False),
        sa.Column("company_name", sa.Text()),
        sa.Column("role", sa.Text(), nullable=False, server_default="user"),
        sa.Column("marketing_consent", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "assessment",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("public_id", sa.Text(), unique=True, nullable=False),
        sa.Column("claim_token", sa.Text(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("user.id")),
        sa.Column("company_name", sa.Text()),
        sa.Column("system_name", sa.Text()),
        sa.Column("email", sa.Text()),
        sa.Column("status", sa.Text(), nullable=False, server_default="draft"),
        sa.Column("rule_version", sa.Integer()),
        sa.Column("source_version", sa.Text()),
        sa.Column("question_set_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("locked_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "assessment_answer",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("assessment_id", sa.BigInteger(), sa.ForeignKey("assessment.id"), nullable=False),
        sa.Column("question_key", sa.Text(), nullable=False),
        sa.Column("answer_value_json", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("assessment_id", "question_key"),
    )

    op.create_table(
        "classification_result",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("assessment_id", sa.BigInteger(), sa.ForeignKey("assessment.id"), unique=True, nullable=False),
        sa.Column("classification_status", sa.Text(), nullable=False),
        sa.Column("risk_tier_id", sa.BigInteger(), sa.ForeignKey("risk_tier.id")),
        sa.Column("actor_role_id", sa.BigInteger(), sa.ForeignKey("actor_role.id")),
        sa.Column("confidence", sa.Text()),
        sa.Column("result_json", postgresql.JSONB(), nullable=False),
        sa.Column("rule_version", sa.Integer(), nullable=False),
        sa.Column("source_version", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "seo_page",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("slug", sa.Text(), unique=True, nullable=False),
        sa.Column("page_type", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), unique=True, nullable=False),
        sa.Column("meta_description", sa.Text(), unique=True, nullable=False),
        sa.Column("content_md", sa.Text(), nullable=False),
        sa.Column("structured_data_json", postgresql.JSONB()),
        sa.Column("canonical_url", sa.Text(), nullable=False),
        sa.Column("last_reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("rule_version", sa.Integer()),
        sa.Column("status", sa.Text(), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("seo_page")
    op.drop_table("classification_result")
    op.drop_table("assessment_answer")
    op.drop_table("assessment")
    op.drop_table("user")
    op.drop_table("obligation")
    op.drop_table("risk_rule")
    op.drop_table("document_type")
    op.drop_index("ix_one_active_ruleset", table_name="rule_set")
    op.drop_table("rule_set")
    op.drop_table("ai_use_case")
    op.drop_table("industry_domain")
    op.drop_table("risk_tier")
    op.drop_table("actor_role")
    op.drop_table("legal_reference")
    op.drop_table("legal_source")
