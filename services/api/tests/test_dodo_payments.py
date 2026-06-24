"""Dodo Payments checkout and webhook behavior."""

from __future__ import annotations

import hashlib
import hmac
import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app import config
from app.models import Entitlement
from app.schemas import CheckoutSessionRequest, GenerateDocumentRequest
from app.services import payment_service


class _ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class _FakeSession:
    def __init__(self, execute_results=None):
        self.added = []
        self.flushed = False
        self.execute_results = list(execute_results or [])

    def add(self, row):
        self.added.append(row)

    async def flush(self):
        self.flushed = True

    async def execute(self, _statement):
        if not self.execute_results:
            raise AssertionError("Unexpected execute call")
        return _ScalarResult(self.execute_results.pop(0))


def _signed_headers(payload: bytes, *, webhook_id: str = "wh_123") -> dict[str, str]:
    timestamp = "1782040000"
    message = b".".join([webhook_id.encode(), timestamp.encode(), payload])
    digest = hmac.new(b"whsec_test", message, hashlib.sha256).hexdigest()
    return {
        "webhook-id": webhook_id,
        "webhook-timestamp": timestamp,
        "webhook-signature": digest,
    }


@pytest.mark.asyncio
async def test_dodo_checkout_creates_pending_entitlement_with_product_metadata(monkeypatch):
    monkeypatch.setattr(config.settings, "dodo_payments_api_key", "dodo_test_key", raising=False)
    monkeypatch.setattr(config.settings, "dodo_payments_environment", "test_mode", raising=False)
    monkeypatch.setattr(
        config.settings, "dodo_product_evidence_pack", "prod_evidence_20", raising=False
    )
    monkeypatch.setattr(config.settings, "stripe_secret_key", None)

    captured = {}

    async def fake_post(path, payload):
        captured["path"] = path
        captured["payload"] = payload
        return {
            "session_id": "checkout_123",
            "checkout_url": "https://test.dodopayments.com/checkout/checkout_123",
        }

    monkeypatch.setattr(payment_service, "_post_dodo", fake_post, raising=False)

    session = _FakeSession()
    result = await payment_service.create_checkout_session(
        session,
        assessment_id=42,
        assessment_public_id="aia_123",
        sku="evidence_pack",
        success_url="https://euaiact.originalnexus.com/checkout/success",
        cancel_url="https://euaiact.originalnexus.com/pricing",
        customer_email="buyer@example.com",
    )

    assert result == {
        "checkout_url": "https://test.dodopayments.com/checkout/checkout_123",
        "session_id": "checkout_123",
    }
    assert captured["path"] == "/checkouts"
    assert captured["payload"]["product_cart"] == [
        {"product_id": "prod_evidence_20", "quantity": 1}
    ]
    assert captured["payload"]["return_url"].startswith(
        "https://euaiact.originalnexus.com/checkout/success"
    )
    assert captured["payload"]["cancel_url"] == "https://euaiact.originalnexus.com/pricing"
    assert captured["payload"]["metadata"] == {
        "assessment_id": "42",
        "assessment_public_id": "aia_123",
        "sku": "evidence_pack",
        "customer_email": "buyer@example.com",
    }
    assert session.flushed
    assert len(session.added) == 1
    entitlement = session.added[0]
    assert isinstance(entitlement, Entitlement)
    assert entitlement.assessment_id == 42
    assert entitlement.sku == "evidence_pack"
    assert entitlement.status == "pending"
    assert entitlement.stripe_checkout_session_id == "checkout_123"


@pytest.mark.asyncio
async def test_dodo_payment_succeeded_activates_matching_entitlement(monkeypatch):
    monkeypatch.setattr(config.settings, "dodo_payments_api_key", "dodo_test_key", raising=False)
    monkeypatch.setattr(config.settings, "dodo_payments_webhook_key", "whsec_test", raising=False)

    entitlement = Entitlement(
        assessment_id=42,
        sku="evidence_pack",
        status="pending",
        stripe_checkout_session_id="checkout_123",
    )
    session = _FakeSession(execute_results=[None, entitlement])
    payload = json.dumps(
        {
            "business_id": "biz_123",
            "type": "payment.succeeded",
            "timestamp": "2026-06-21T12:00:00Z",
            "data": {
                "payload_type": "Payment",
                "payment_id": "pay_123",
                "checkout_session_id": "checkout_123",
                "customer": {"customer_id": "cust_123"},
                "metadata": {
                    "assessment_id": "42",
                    "assessment_public_id": "aia_123",
                    "sku": "evidence_pack",
                },
            },
        },
        separators=(",", ":"),
    ).encode()

    handled = await payment_service.handle_dodo_webhook(
        session, payload, _signed_headers(payload, webhook_id="wh_activated")
    )

    assert handled is True
    assert entitlement.status == "active"
    assert entitlement.stripe_customer_id == "cust_123"
    assert session.flushed
    event = session.added[0]
    assert event.stripe_event_id == "wh_activated"
    assert event.type == "payment.succeeded"


@pytest.mark.asyncio
async def test_dodo_webhook_replay_is_idempotent(monkeypatch):
    monkeypatch.setattr(config.settings, "dodo_payments_api_key", "dodo_test_key", raising=False)
    monkeypatch.setattr(config.settings, "dodo_payments_webhook_key", "whsec_test", raising=False)

    payload = json.dumps(
        {
            "business_id": "biz_123",
            "type": "payment.succeeded",
            "timestamp": "2026-06-21T12:00:00Z",
            "data": {"payload_type": "Payment", "checkout_session_id": "checkout_123"},
        },
        separators=(",", ":"),
    ).encode()
    existing_event = SimpleNamespace(stripe_event_id="wh_replay")
    session = _FakeSession(execute_results=[existing_event])

    handled = await payment_service.handle_dodo_webhook(
        session, payload, _signed_headers(payload, webhook_id="wh_replay")
    )

    assert handled is True
    assert session.added == []
    assert session.flushed is False


def test_dodo_webhook_signature_ignores_secret_manager_trailing_newline(monkeypatch):
    monkeypatch.setattr(config.settings, "dodo_payments_webhook_key", "whsec_test\n")
    payload = b'{"type":"payment.succeeded","data":{"payload_type":"Payment"}}'

    event = payment_service._verify_dodo_signature(payload, _signed_headers(payload))

    assert event["type"] == "payment.succeeded"


def test_starter_report_sku_is_not_accepted():
    with pytest.raises(ValidationError):
        CheckoutSessionRequest(
            assessment_id="aia_123",
            sku="starter_report",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )

    with pytest.raises(ValidationError):
        GenerateDocumentRequest(assessment_id="aia_123", sku="starter_report")


@pytest.mark.asyncio
async def test_prod_without_payment_provider_never_auto_grants(monkeypatch):
    monkeypatch.setattr(config.settings, "dev_mode", False, raising=False)
    monkeypatch.setattr(config.settings, "dodo_payments_api_key", None, raising=False)
    monkeypatch.setattr(config.settings, "stripe_secret_key", None, raising=False)

    session = _FakeSession()

    with pytest.raises(RuntimeError, match="Payment provider not configured"):
        await payment_service.create_checkout_session(
            session,
            assessment_id=42,
            assessment_public_id="aia_123",
            sku="evidence_pack",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            customer_email=None,
        )

    assert session.added == []
    assert session.flushed is False
