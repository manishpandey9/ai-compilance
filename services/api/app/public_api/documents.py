from datetime import UTC

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dal.assessments import get_assessment_by_public_id
from app.db import get_db
from app.models import DownloadToken, Entitlement, GeneratedDocument, ReportJob
from app.schemas import (
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    GenerateDocumentRequest,
    GenerateDocumentResponse,
    ReportStatusResponse,
)
from app.services.document_service import (
    create_download_token,
    enqueue_generation,
    get_active_entitlement,
    should_schedule_generation,
)
from app.services.payment_service import create_checkout_session
from app.storage import download_bytes
from app.workers.generate_document import run_generate_document

router = APIRouter(tags=["documents", "payments"])


def unique_report_documents(docs: list[GeneratedDocument]) -> list[GeneratedDocument]:
    """Collapse duplicate artifact rows by final filename, preserving latest rows."""
    by_name: dict[str, GeneratedDocument] = {}
    for doc in docs:
        by_name[doc.file_path.rsplit("/", 1)[-1]] = doc
    return list(by_name.values())


@router.post("/checkout/session", response_model=CheckoutSessionResponse)
async def checkout_session(
    body: CheckoutSessionRequest,
    db: AsyncSession = Depends(get_db),
) -> CheckoutSessionResponse:
    assessment = await get_assessment_by_public_id(db, body.assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Assessment not found", "details": []}})
    if body.customer_email is not None:
        assessment.email = body.customer_email
    result = await create_checkout_session(
        db,
        assessment_id=assessment.id,
        assessment_public_id=assessment.public_id,
        sku=body.sku,
        success_url=body.success_url,
        cancel_url=body.cancel_url,
        customer_email=body.customer_email or assessment.email,
    )
    return CheckoutSessionResponse(**result)


@router.post("/documents/generate", response_model=GenerateDocumentResponse, status_code=202)
async def generate_documents(
    body: GenerateDocumentRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> GenerateDocumentResponse:
    assessment = await get_assessment_by_public_id(db, body.assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Assessment not found", "details": []}})

    ent = await get_active_entitlement(db, assessment.id, body.sku)
    if not ent:
        raise HTTPException(
            status_code=403,
            detail={"error": {"code": "entitlement_required", "message": "Purchase required", "details": []}},
        )

    job, created = await enqueue_generation(db, assessment, body.sku)
    await db.commit()
    if should_schedule_generation(job, created=created):
        background_tasks.add_task(run_generate_document, job.report_id)
    return GenerateDocumentResponse(report_id=job.report_id, status=job.status)


@router.get("/documents/{report_id}", response_model=ReportStatusResponse)
async def get_report_status(
    report_id: str,
    db: AsyncSession = Depends(get_db),
) -> ReportStatusResponse:
    job_result = await db.execute(select(ReportJob).where(ReportJob.report_id == report_id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Report not found", "details": []}})

    docs_result = await db.execute(
        select(GeneratedDocument).where(GeneratedDocument.report_id == report_id)
    )
    docs = unique_report_documents(docs_result.scalars().all())
    artifacts = []
    for doc in docs:
        token = await create_download_token(db, doc.assessment_id, doc.file_path)
        artifacts.append(
            {
                "document_type": doc.file_path.rsplit("/", 1)[-1],
                "format": doc.format,
                "download": f"/api/v1/downloads/{token}",
            }
        )

    return ReportStatusResponse(
        report_id=job.report_id,
        status=job.status,
        rule_version=job.rule_version,
        source_version=job.source_version,
        artifacts=artifacts,
        error=job.error_message,
    )


@router.get("/downloads/{token}")
async def download_file(token: str, db: AsyncSession = Depends(get_db)):
    from datetime import datetime

    result = await db.execute(select(DownloadToken).where(DownloadToken.token == token))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found", "message": "Invalid token", "details": []}})
    if row.expires_at < datetime.now(UTC):
        entitlement = (
            await db.execute(
                select(Entitlement).where(
                    Entitlement.assessment_id == row.assessment_id,
                    Entitlement.status == "active",
                )
            )
        ).scalar_one_or_none()
        if not entitlement:
            raise HTTPException(status_code=410, detail={"error": {"code": "gone", "message": "Download link expired", "details": []}})

    data = download_bytes(row.file_path)
    filename = row.file_path.rsplit("/", 1)[-1]
    return StreamingResponse(
        iter([data]),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    from app.services.payment_service import handle_stripe_webhook

    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    await handle_stripe_webhook(db, payload, sig)
    return {"received": True}


@router.post("/dodo/webhook")
async def dodo_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    from app.services.payment_service import handle_dodo_webhook

    payload = await request.body()
    headers = {
        "webhook-id": request.headers.get("webhook-id", ""),
        "webhook-signature": request.headers.get("webhook-signature", ""),
        "webhook-timestamp": request.headers.get("webhook-timestamp", ""),
    }
    try:
        await handle_dodo_webhook(db, payload, headers)
    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "invalid_signature", "message": str(exc), "details": []}},
        ) from exc
    return {"received": True}
