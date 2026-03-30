from __future__ import annotations

import hmac
import time
from typing import Optional

from fastapi import HTTPException
from bridgexapi import BridgeXAPI

from app.config import settings
from app.models import OTPRecord
from app.otp.store import store
from app.otp.utils import generate_otp, hash_otp, mask_number, record_key
from app.schemas import SendOTPRequest, SendOTPResponse, VerifyOTPRequest, VerifyOTPResponse

client = BridgeXAPI(
    api_key=settings.bridgexapi_api_key,
    base_url=settings.bridgexapi_base_url,
    timeout=settings.bridgexapi_timeout,
)


def _extract_bridge_ids(result) -> tuple[Optional[str], Optional[str]]:
    bx_message_id = None
    order_id = None

    if hasattr(result, "order_id"):
        order_id = result.order_id

    if hasattr(result, "messages") and result.messages:
        first = result.messages[0]
        if hasattr(first, "bx_message_id"):
            bx_message_id = first.bx_message_id

    return bx_message_id, order_id


def _build_delivery_status_url(bx_message_id: Optional[str]) -> Optional[str]:
    if not bx_message_id:
        return None
    return f"{settings.bridgexapi_base_url}/api/v1/dlr/{bx_message_id}"


def send_otp(payload: SendOTPRequest) -> SendOTPResponse:
    store.cleanup()

    key = record_key(payload.phone_number, payload.purpose)
    now = int(time.time())
    existing = store.get(key)

    if existing and existing.last_sent_at + settings.otp_send_cooldown_seconds > now:
        retry_after = (existing.last_sent_at + settings.otp_send_cooldown_seconds) - now
        raise HTTPException(
            status_code=429,
            detail=f"OTP was sent too recently. Retry in {retry_after} seconds.",
        )

    code = generate_otp()
    message = f"Your verification code is {code}."

    try:
        result = client.send_sms(
            route_id=payload.route_id,
            caller_id=settings.default_caller_id,
            numbers=[payload.phone_number],
            message=message,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"SMS send failed: {exc}") from exc

    bx_message_id, order_id = _extract_bridge_ids(result)

    record = OTPRecord(
        phone_number=payload.phone_number,
        otp_hash=hash_otp(payload.phone_number, payload.purpose, code),
        expires_at=now + settings.otp_ttl_seconds,
        attempts_left=settings.otp_max_attempts,
        last_sent_at=now,
        purpose=payload.purpose,
        route_id=payload.route_id,
    )
    store.set(key, record)

    return SendOTPResponse(
        status="otp_sent",
        phone_number=mask_number(payload.phone_number),
        purpose=payload.purpose,
        route_id=payload.route_id,
        expires_in_seconds=settings.otp_ttl_seconds,
        cooldown_seconds=settings.otp_send_cooldown_seconds,
        debug_code=code if settings.debug_otp else None,
        bx_message_id=str(bx_message_id) if bx_message_id is not None else None,
        order_id=str(order_id) if order_id is not None else None,
        delivery_status_url=_build_delivery_status_url(
            str(bx_message_id) if bx_message_id is not None else None
        ),
    )


def verify_otp(payload: VerifyOTPRequest) -> VerifyOTPResponse:
    store.cleanup()

    key = record_key(payload.phone_number, payload.purpose)
    record = store.get(key)

    if not record:
        raise HTTPException(
            status_code=404,
            detail="No active OTP found for this phone number and purpose.",
        )

    if record.attempts_left <= 0:
        store.delete(key)
        raise HTTPException(status_code=429, detail="OTP attempts exceeded.")

    expected_hash = hash_otp(payload.phone_number, payload.purpose, payload.code)

    if not hmac.compare_digest(record.otp_hash, expected_hash):
        record.attempts_left -= 1
        store.set(key, record)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid OTP. Attempts left: {record.attempts_left}",
        )

    store.delete(key)

    return VerifyOTPResponse(
        status="otp_verified",
        phone_number=mask_number(payload.phone_number),
        purpose=payload.purpose,
        verified=True,
    )