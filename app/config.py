from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name, str(default)).strip().lower()
    return value in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = "BridgeXAPI OTP Server"
    app_version: str = "1.0.0"

    otp_length: int = int(os.getenv("OTP_LENGTH", "6"))
    otp_ttl_seconds: int = int(os.getenv("OTP_TTL_SECONDS", "300"))
    otp_send_cooldown_seconds: int = int(os.getenv("OTP_SEND_COOLDOWN_SECONDS", "45"))
    otp_max_attempts: int = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))

    default_route_id: int = int(os.getenv("DEFAULT_ROUTE_ID", "3"))
    default_caller_id: str = os.getenv("DEFAULT_CALLER_ID", "BRIDGEXAPI").strip()

    bridgexapi_api_key: str = os.getenv("BRIDGEXAPI_API_KEY", "").strip()
    bridgexapi_base_url: str = os.getenv("BRIDGEXAPI_BASE_URL", "https://hi.bridgexapi.io").strip()
    bridgexapi_timeout: float = float(os.getenv("BRIDGEXAPI_TIMEOUT", "20"))

    otp_hmac_secret: bytes = os.getenv("OTP_HMAC_SECRET", "change-me-in-production").encode()
    api_auth_token: str = os.getenv("API_AUTH_TOKEN", "").strip()
    debug_otp: bool = _get_bool("DEBUG_OTP", False)


settings = Settings()

if not settings.bridgexapi_api_key:
    raise RuntimeError("BRIDGEXAPI_API_KEY is required.")

if not settings.default_caller_id:
    raise RuntimeError("DEFAULT_CALLER_ID is required.")

if settings.otp_length < 4 or settings.otp_length > 10:
    raise RuntimeError("OTP_LENGTH must be between 4 and 10.")

if settings.otp_ttl_seconds < 30:
    raise RuntimeError("OTP_TTL_SECONDS must be at least 30 seconds.")

if settings.otp_max_attempts < 1:
    raise RuntimeError("OTP_MAX_ATTEMPTS must be at least 1.")