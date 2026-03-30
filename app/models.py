from __future__ import annotations

from dataclasses import dataclass


@dataclass
class OTPRecord:
    phone_number: str
    otp_hash: str
    expires_at: int
    attempts_left: int
    last_sent_at: int
    purpose: str
    route_id: int