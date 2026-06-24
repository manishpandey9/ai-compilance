"""Checkout and webhook handling for payment providers."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import httpx
import stripe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.services.email_service import send_purchase_receipt

if TYPE_CHECKING:
    from app.models import Entitlement

EVIDENCE_PACK_SKU = "evidence_pack"
EVIDENCE_PACK_PRICE_CENTS = 2000
SUPPORTED_SKUS = {EVIDENCE_PACK_SKU}


def _stripe_configured() -> bool:
    return bool(settings.stripe_secret_key)


def _dodo_configured() -> bool:
    return bool(settings.dodo_payments_api_key)


def _dodo_api_key() -> str:
    return (settings.dodo_payments_api_key or "").strip()


def _dodo_webhook_key() -> str:
    return (settings.dodo_payments_webhook_key or "").strip()


def _dodo_base_url() -> str:
    if settings.dodo_payments_environment == "test_mode":
        return "https://test.dodopayments.com"
    return "https://live.dodopayments.com"


def _dodo_product_id(sku: str) -> str:
    product_map = {EVIDENCE_PACK_SKU: settings.dodo_product_evidence_pack}
    product_id = product_map.get(sku)
    if not product_id:
        raise ValueError(f"No Dodo product configured for {sku}")
    return product_id


async def _post_dodo(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            f"{_dodo_base_url()}{path}",
            headers={
                "Authorization": f"Bearer {_dodo_api_key()}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        return response.json()


def _append_checkout_params(url: str, *, assessment_public_id: str, sku: str) -> str:
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}assessment_id={assessment_public_id}&sku={sku}"


def _verify_dodo_signature(payload: bytes, headers: dict[str, str]) -> dict[str, Any]:
    webhook_id = headers.get("webhook-id", "")
    timestamp = headers.get("webhook-timestamp", "")
    signature = headers.get("webhook-signature", "")
    webhook_key = _dodo_webhook_key()
    if not webhook_id or not timestamp or not signature or not webhook_key:
        raise ValueError("Missing Dodo webhook signature headers")

    signed_payload = b".".join([webhook_id.encode(), timestamp.encode(), payload])
    digest = hmac.new(webhook_key.encode(), signed_payload, hashlib.sha256).digest()
    hex_digest = digest.hex()
    b64_digest = base64.b64encode(digest).decode()
    b64_digest_unpadded = b64_digest.rstrip("=")
    valid_signatures = {
        hex_digest,
        b64_digest,
        b64_digest_unpadded,
        f"v1,{hex_digest}",
        f"v1,{b64_digest}",
        f"v1,{b64_digest_unpadded}",
    }
    if not any(hmac.compare_digest(signature, candidate) for candidate in valid_signatures):
        raise ValueError("Invalid Dodo webhook signature")
    return json.loads(payload.decode())


def _dodo_customer_id(data: dict[str, Any]) -> str | None:
    customer = data.get("customer")
    if isinstance(customer, dict):
        return customer.get("customer_id") or customer.get("id")
    return data.get("customer_id")


async def create_checkout_session(
    session: AsyncSession,
    *,
    assessment_id: int,
    assessment_public_id: str,
    sku: str,
    success_url: str,
    cancel_url: str,
    customer_email: str | None = None,
) -> dict[str, str]:
    from app.models import Entitlement

    if sku not in SUPPORTED_SKUS:
        raise ValueError(f"Unknown SKU: {sku}")

    if _dodo_configured():
        product_id = _dodo_product_id(sku)
        metadata = {
            "assessment_id": str(assessment_id),
            "assessment_public_id": assessment_public_id,
            "sku": sku,
        }
        if customer_email:
            metadata["customer_email"] = customer_email
        checkout = await _post_dodo(
            "/checkouts",
            {
                "product_cart": [{"product_id": product_id, "quantity": 1}],
                "return_url": _append_checkout_params(
                    success_url, assessment_public_id=assessment_public_id, sku=sku
                ),
                "cancel_url": cancel_url,
                "metadata": metadata,
            },
        )
        session_id = checkout["session_id"]
        ent = Entitlement(
            assessment_id=assessment_id,
            sku=sku,
            status="pending",
            stripe_checkout_session_id=session_id,
        )
        session.add(ent)
        await session.flush()
        return {"checkout_url": checkout["checkout_url"], "session_id": session_id}

    if not _stripe_configured():
        if not settings.dev_mode:
            raise RuntimeError("Payment provider not configured")
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
    price_map = {EVIDENCE_PACK_SKU: settings.stripe_price_evidence_pack}
    price_id = price_map.get(sku)
    if not price_id:
        raise ValueError(f"No Stripe price configured for {sku}")

    checkout = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "assessment_id": str(assessment_id),
            "assessment_public_id": assessment_public_id,
            "sku": sku,
            "customer_email": customer_email or "",
        },
        customer_email=customer_email,
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


async def handle_dodo_webhook(
    session: AsyncSession, payload: bytes, headers: dict[str, str]
) -> bool:
    from app.models import Entitlement, StripeEvent

    if not _dodo_configured():
        return False

    event = _verify_dodo_signature(payload, headers)
    webhook_id = headers["webhook-id"]
    event_type = event.get("type", "")
    data = event.get("data") or {}
    if not isinstance(data, dict):
        data = {}

    existing = await session.execute(
        select(StripeEvent).where(StripeEvent.stripe_event_id == webhook_id)
    )
    if existing.scalar_one_or_none():
        return True

    session.add(
        StripeEvent(
            stripe_event_id=webhook_id,
            type=event_type,
            payload_json=event,
            processed_at=datetime.now(UTC),
        )
    )

    if event_type == "payment.succeeded":
        checkout_session_id = data.get("checkout_session_id") or data.get("checkout_id")
        ent = None
        if checkout_session_id:
            ent_result = await session.execute(
                select(Entitlement).where(
                    Entitlement.stripe_checkout_session_id == checkout_session_id
                )
            )
            ent = ent_result.scalar_one_or_none()

        metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
        if ent is None and metadata.get("assessment_id") and metadata.get("sku"):
            ent_result = await session.execute(
                select(Entitlement).where(
                    Entitlement.assessment_id == int(metadata["assessment_id"]),
                    Entitlement.sku == metadata["sku"],
                )
            )
            ent = ent_result.scalar_one_or_none()

        if ent:
            ent.status = "active"
            ent.stripe_customer_id = _dodo_customer_id(data)
            await send_purchase_receipt(
                to_email=metadata.get("customer_email"),
                assessment_public_id=metadata.get("assessment_public_id"),
                sku=ent.sku,
            )

    await session.flush()
    return True


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
            processed_at=datetime.now(UTC),
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
            metadata = cs.metadata or {}
            await send_purchase_receipt(
                to_email=metadata.get("customer_email"),
                assessment_public_id=metadata.get("assessment_public_id"),
                sku=ent.sku,
            )

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
