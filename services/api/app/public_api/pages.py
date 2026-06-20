from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.data.pseo_catalog import is_index_supported
from app.models import LegalReference, SEOPage, SEOPageReference
from app.schemas import SEOPageResponse

router = APIRouter(prefix="/pages", tags=["pages"])


@router.get("")
async def list_pages(
    type: str | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    q = select(SEOPage).where(SEOPage.status == "active").limit(min(limit, 100))
    if type:
        q = q.where(SEOPage.page_type == type)
    result = await db.execute(q)
    pages = result.scalars().all()
    return {
        "data": [
            {
                "slug": p.slug,
                "title": p.title,
                "page_type": p.page_type,
                "last_reviewed_at": p.last_reviewed_at,
                "index_supported": is_index_supported(p.slug),
            }
            for p in pages
        ]
    }


@router.get("/{slug:path}", response_model=SEOPageResponse)
async def get_page(slug: str, db: AsyncSession = Depends(get_db)) -> SEOPageResponse:
    result = await db.execute(
        select(SEOPage).where(SEOPage.slug == slug, SEOPage.status == "active")
    )
    page = result.scalar_one_or_none()
    if not page:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "not_found", "message": "Page not found", "details": []}},
        )
    structured = page.structured_data_json
    if isinstance(structured, dict):
        structured = [structured]

    refs_result = await db.execute(
        select(LegalReference)
        .join(SEOPageReference, SEOPageReference.legal_reference_id == LegalReference.id)
        .where(SEOPageReference.seo_page_id == page.id)
    )
    references = [
        {"canonical_citation": r.canonical_citation, "url": r.url_fragment or ""}
        for r in refs_result.scalars().all()
    ]

    return SEOPageResponse(
        slug=page.slug,
        page_type=page.page_type,
        title=page.title,
        meta_description=page.meta_description,
        content_md=page.content_md,
        structured_data=structured,
        canonical_url=page.canonical_url,
        last_reviewed_at=page.last_reviewed_at,
        rule_version=page.rule_version,
        index_supported=is_index_supported(page.slug),
        references=references,
    )
