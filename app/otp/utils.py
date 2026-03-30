from __future__ import annotations

import hashlib
import hmac
import secrets

from app.config import settings


def generate_otp() -> str:
    digits = "0123456789"
    return "".join(secrets.choice(digits) for _ in range(settings.otp_length))


def hash_otp(phone_number: str, purpose: str, code: str) -> str:
    message = f"{purpose}:{phone_number}:{code}".encode()
    return hmac.new(settings.otp_hmac_secret, message, hashlib.sha256).hexdigest()


def mask_number(phone_number: str) -> str:
    if len(phone_number) <= 4:
        return phone_number
    return f"{'*' * (len(phone_number) - 4)}{phone_number[-4:]}"


def record_key(phone_number: str, purpose: str) -> str:
    return f"{purpose}:{phone_number}"