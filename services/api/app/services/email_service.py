"""Transactional email helpers.

Email is best-effort: when no provider key is configured, calls are no-ops so
local development and tests do not depend on external services.
"""

from __future__ import annotations

import httpx

from app.config import settings


async def send_purchase_receipt(
    *,
    to_email: str | None,
    assessment_public_id: str | None,
    sku: str,
) -> None:
    if not settings.resend_api_key or not to_email or not assessment_public_id:
        return

    link = (
        f"{settings.web_base_url}/checkout/success"
        f"?assessment_id={assessment_public_id}&sku={sku}"
    )
    async with httpx.AsyncClient(timeout=15) as client:
        await client.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {settings.resend_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": settings.transactional_from_email,
                "to": [to_email],
                "subject": "Your EU AI Act evidence-prep pack receipt",
                "text": (
                    "Payment received for your EU AI Act evidence-prep pack.\n\n"
                    f"Use this link to generate or re-open your documents: {link}\n\n"
                    "This pack is an evidence-preparation draft, not legal advice."
                ),
            },
        )
