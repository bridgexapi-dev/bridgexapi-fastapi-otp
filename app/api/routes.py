from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.config import settings
from app.otp.service import send_otp, verify_otp
from app.otp.store import store
from app.schemas import SendOTPRequest, SendOTPResponse, VerifyOTPRequest, VerifyOTPResponse

router = APIRouter()


def require_api_token(request: Request) -> None:
    if not settings.api_auth_token:
        return

    auth_header = request.headers.get("authorization", "")
    expected = f"Bearer {settings.api_auth_token}"

    if auth_header != expected:
        raise HTTPException(status_code=401, detail="Unauthorized.")


@router.get("/health")
def health() -> dict:
    store.cleanup()
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "active_otps": len(store.records),
    }


@router.get("/config")
def config(request: Request) -> dict:
    require_api_token(request)
    return {
        "otp_length": settings.otp_length,
        "otp_ttl_seconds": settings.otp_ttl_seconds,
        "otp_send_cooldown_seconds": settings.otp_send_cooldown_seconds,
        "otp_max_attempts": settings.otp_max_attempts,
        "default_route_id": settings.default_route_id,
        "default_caller_id": settings.default_caller_id,
        "debug_otp": settings.debug_otp,
    }


@router.post("/send-otp", response_model=SendOTPResponse)
def send_otp_route(payload: SendOTPRequest, request: Request) -> SendOTPResponse:
    require_api_token(request)
    return send_otp(payload)


@router.post("/verify-otp", response_model=VerifyOTPResponse)
def verify_otp_route(payload: VerifyOTPRequest, request: Request) -> VerifyOTPResponse:
    require_api_token(request)
    return verify_otp(payload)