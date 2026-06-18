"""Document generation orchestration."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from ulid import ULID

from app.config import settings
from app.documents.context_builder import build_render_context
from app.documents.pack import build_pack_files
from app.documents.renderers import build_zip
from app.models import (
    Assessment,
    ClassificationResult,
    DownloadToken,
    Entitlement,
    GeneratedDocument,
    ReportJob,
)
from app.storage import checksum, upload_bytes


def _report_id() -> str:
    return f"rep_{ULID()}"


def _download_token() -> str:
    return f"sig_{secrets.token_urlsafe(32)}"


async def get_active_entitlement(
    session: AsyncSession, assessment_id: int, sku: str
) -> Entitlement | None:
    result = await session.execute(
        select(Entitlement).where(
            Entitlement.assessment_id == assessment_id,
            Entitlement.sku == sku,
            Entitlement.status == "active",
        )
    )
    return result.scalar_one_or_none()


async def enqueue_generation(
    session: AsyncSession, assessment: Assessment, sku: str
) -> ReportJob:
    existing = await session.execute(
        select(ReportJob).where(ReportJob.assessment_id == assessment.id, ReportJob.sku == sku)
    )
    job = existing.scalar_one_or_none()
    if job:
        return job

    job = ReportJob(
        report_id=_report_id(),
        assessment_id=assessment.id,
        sku=sku,
        status="queued",
        rule_version=assessment.rule_version,
        source_version=assessment.source_version,
    )
    session.add(job)
    await session.flush()
    return job


def run_generation_sync(session: Session, report_id: str) -> None:
    """Generate documents synchronously (worker or background task)."""
    job = session.execute(select(ReportJob).where(ReportJob.report_id == report_id)).scalar_one()
    job.status = "generating"
    session.commit()

    try:
        assessment = session.get(Assessment, job.assessment_id)
        if not assessment:
            raise ValueError("Assessment not found")

        classification = session.execute(
            select(ClassificationResult).where(ClassificationResult.assessment_id == assessment.id)
        ).scalar_one_or_none()
        if not classification:
            raise ValueError("Classification required before document generation")

        ctx = build_render_context(
            session,
            assessment=assessment,
            classification=classification,
            pack_sku=job.sku,
        )

        files = build_pack_files(ctx, job.sku)
        zip_name = "evidence_pack.zip" if job.sku == "evidence_pack" else "starter_report.zip"
        zip_data = build_zip(files)

        prefix = f"reports/{assessment.public_id}/{report_id}"
        for fname, data in files.items():
            key = f"{prefix}/{fname}"
            upload_bytes(key, data, _content_type(fname))
            session.add(
                GeneratedDocument(
                    assessment_id=assessment.id,
                    report_id=report_id,
                    file_path=key,
                    format=fname.rsplit(".", 1)[-1],
                    checksum=checksum(data),
                    rule_version=classification.rule_version,
                    source_version=classification.source_version,
                )
            )

        zip_key = f"{prefix}/{zip_name}"
        upload_bytes(zip_key, zip_data, "application/zip")
        session.add(
            GeneratedDocument(
                assessment_id=assessment.id,
                report_id=report_id,
                file_path=zip_key,
                format="zip",
                checksum=checksum(zip_data),
                rule_version=classification.rule_version,
                source_version=classification.source_version,
            )
        )

        assessment.locked_at = datetime.now(timezone.utc)
        job.status = "ready"
        session.commit()
    except Exception as exc:
        job.status = "failed"
        job.error_message = str(exc)
        session.commit()
        raise


def _content_type(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()
    return {
        "md": "text/markdown",
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "csv": "text/csv",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "zip": "application/zip",
    }.get(ext, "application/octet-stream")


async def create_download_token(
    session: AsyncSession, assessment_id: int, file_path: str
) -> str:
    token = _download_token()
    session.add(
        DownloadToken(
            token=token,
            file_path=file_path,
            assessment_id=assessment_id,
            expires_at=datetime.now(timezone.utc)
            + timedelta(seconds=settings.download_token_ttl_seconds),
        )
    )
    await session.flush()
    return token
