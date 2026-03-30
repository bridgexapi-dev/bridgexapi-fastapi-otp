from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.config import settings


class SendOTPRequest(BaseModel):
    phone_number: str = Field(..., description="Digits-only destination number.")
    purpose: str = Field(default="login", description="Business purpose for the OTP.")
    route_id: int = Field(default=settings.default_route_id, ge=1, le=8)

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        value = value.strip()
        if not value.isdigit():
            raise ValueError("phone_number must contain digits only.")
        if len(value) < 10 or len(value) > 15:
            raise ValueError("phone_number must usually be between 10 and 15 digits.")
        return value

    @field_validator("purpose")
    @classmethod
    def validate_purpose(cls, value: str) -> str:
        value = value.strip().lower()
        if not value:
            raise ValueError("purpose cannot be empty.")
        if len(value) > 50:
            raise ValueError("purpose must be 50 characters or less.")
        return value


class VerifyOTPRequest(BaseModel):
    phone_number: str
    code: str
    purpose: str = "login"

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        value = value.strip()
        if not value.isdigit():
            raise ValueError("phone_number must contain digits only.")
        return value

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        value = value.strip()
        if not value.isdigit():
            raise ValueError("code must be numeric.")
        return value

    @field_validator("purpose")
    @classmethod
    def validate_purpose(cls, value: str) -> str:
        value = value.strip().lower()
        if not value:
            raise ValueError("purpose cannot be empty.")
        return value


class SendOTPResponse(BaseModel):
    status: str
    phone_number: str
    purpose: str
    route_id: int
    expires_in_seconds: int
    cooldown_seconds: int
    debug_code: Optional[str] = None
    bx_message_id: Optional[str] = None
    order_id: Optional[str] = None
    delivery_status_url: Optional[str] = None


class VerifyOTPResponse(BaseModel):
    status: str
    phone_number: str
    purpose: str
    verified: bool