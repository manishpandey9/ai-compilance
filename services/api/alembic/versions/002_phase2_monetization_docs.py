"""Phase 2 tables: entitlements, documents, downloads, audit."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "document_template",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("document_type_id", sa.BigInteger(), sa.ForeignKey("document_type.id"), nullable=False),
        sa.Column("template_name", sa.Text(), nullable=False),
        sa.Column("template_body", sa.Text(), nullable=False),
        sa.Column("variables_schema_json", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.Text(), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("document_type_id", "template_name", "version"),
    )

    op.create_table(
        "report_job",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("report_id", sa.Text(), unique=True, nullable=False),
        sa.Column("assessment_id", sa.BigInteger(), sa.ForeignKey("assessment.id"), nullable=False),
        sa.Column("sku", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="queued"),
        sa.Column("error_message", sa.Text()),
        sa.Column("rule_version", sa.Integer()),
        sa.Column("source_version", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "generated_document",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("assessment_id", sa.BigInteger(), sa.ForeignKey("assessment.id"), nullable=False),
        sa.Column("report_id", sa.Text(), nullable=False),
        sa.Column("document_type_id", sa.BigInteger(), sa.ForeignKey("document_type.id")),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("format", sa.Text(), nullable=False),
        sa.Column("checksum", sa.Text()),
        sa.Column("rule_version", sa.Integer(), nullable=False),
        sa.Column("source_version", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "download_token",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("token", sa.Text(), unique=True, nullable=False),
        sa.Column("file_path", sa.Text(), nullable=False),
        sa.Column("assessment_id", sa.BigInteger(), sa.ForeignKey("assessment.id"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "entitlement",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), sa.ForeignKey("user.id")),
        sa.Column("assessment_id", sa.BigInteger(), sa.ForeignKey("assessment.id"), nullable=False),
        sa.Column("sku", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="pending"),
        sa.Column("stripe_customer_id", sa.Text()),
        sa.Column("stripe_subscription_id", sa.Text()),
        sa.Column("stripe_checkout_session_id", sa.Text(), unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "stripe_event",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("stripe_event_id", sa.Text(), unique=True, nullable=False),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("payload_json", postgresql.JSONB()),
        sa.Column("processed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "seo_page_reference",
        sa.Column("seo_page_id", sa.BigInteger(), sa.ForeignKey("seo_page.id"), primary_key=True),
        sa.Column("legal_reference_id", sa.BigInteger(), sa.ForeignKey("legal_reference.id"), primary_key=True),
    )

    op.create_table(
        "audit_log",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("actor_email", sa.Text(), nullable=False),
        sa.Column("action", sa.Text(), nullable=False),
        sa.Column("entity_type", sa.Text(), nullable=False),
        sa.Column("entity_id", sa.Text(), nullable=False),
        sa.Column("details_json", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("seo_page_reference")
    op.drop_table("stripe_event")
    op.drop_table("entitlement")
    op.drop_table("download_token")
    op.drop_table("generated_document")
    op.drop_table("report_job")
    op.drop_table("document_template")
