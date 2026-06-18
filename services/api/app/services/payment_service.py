"""Stripe checkout and webhook handling."""

from __future__ import annotations

import secrets
from datetime import datetime, timezone

import stripe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings

SKU_PRICES = {
    "starter_report": ("Starter Report", 19900),
    "evidence_pack": ("Evidence Pack", 69900),
}


def _stripe_configured() -> bool:
    return bool(settings.stripe_secret_key)


async def create_checkout_session(
    session: AsyncSession,
    *,
    assessment_id: int,
    assessment_public_id: str,
    sku: str,
    success_url: str,
    cancel_url: str,
) -> dict[str, str]:
    from app.models import Entitlement

    if sku not in SKU_PRICES:
        raise ValueError(f"Unknown SKU: {sku}")

    if not _stripe_configured():
        if not settings.dev_mode:
            raise RuntimeError("Stripe not configured")
        session_id = f"cs_dev_{secrets.token_hex(12)}"
        ent = Entitlement(
            assessment_id=assessment_id,
            sku=sku,
            status="active",
            stripe_checkout_session_id=session_id,
        )
        session.add(ent)
        await session.flush()
        dev_url = (
            f"{success_url}?session_id={session_id}"
            f"&assessment_id={assessment_public_id}&sku={sku}&dev=1"
        )
        return {"checkout_url": dev_url, "session_id": session_id}

    stripe.api_key = settings.stripe_secret_key
    price_map = {
        "starter_report": settings.stripe_price_starter_report,
        "evidence_pack": settings.stripe_price_evidence_pack,
    }
    price_id = price_map.get(sku)
    if not price_id:
        raise ValueError(f"No Stripe price configured for {sku}")

    checkout = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"assessment_id": str(assessment_id), "sku": sku},
    )

    ent = Entitlement(
        assessment_id=assessment_id,
        sku=sku,
        status="pending",
        stripe_checkout_session_id=checkout.id,
    )
    session.add(ent)
    await session.flush()
    return {"checkout_url": checkout.url, "session_id": checkout.id}


async def handle_stripe_webhook(session: AsyncSession, payload: bytes, sig_header: str) -> bool:
    from app.models import Entitlement, StripeEvent

    if not _stripe_configured():
        return False

    stripe.api_key = settings.stripe_secret_key
    event = stripe.Webhook.construct_event(
        payload, sig_header, settings.stripe_webhook_secret or ""
    )

    existing = await session.execute(
        select(StripeEvent).where(StripeEvent.stripe_event_id == event.id)
    )
    if existing.scalar_one_or_none():
        return True

    session.add(
        StripeEvent(
            stripe_event_id=event.id,
            type=event.type,
            payload_json=dict(event),
            processed_at=datetime.now(timezone.utc),
        )
    )

    if event.type == "checkout.session.completed":
        cs = event.data.object
        ent_result = await session.execute(
            select(Entitlement).where(Entitlement.stripe_checkout_session_id == cs.id)
        )
        ent = ent_result.scalar_one_or_none()
        if ent:
            ent.status = "active"
            ent.stripe_customer_id = cs.customer

    await session.flush()
    return True


async def activate_dev_entitlement(
    session: AsyncSession, session_id: str
) -> Entitlement | None:
    from app.models import Entitlement

    result = await session.execute(
        select(Entitlement).where(Entitlement.stripe_checkout_session_id == session_id)
    )
    ent = result.scalar_one_or_none()
    if ent:
        ent.status = "active"
        await session.flush()
    return ent
