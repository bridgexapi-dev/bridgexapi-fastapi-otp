from __future__ import annotations

import time
from typing import Dict, Optional

from app.models import OTPRecord


class OTPStore:
    def __init__(self) -> None:
        self.records: Dict[str, OTPRecord] = {}

    def get(self, key: str) -> Optional[OTPRecord]:
        record = self.records.get(key)
        if record and record.expires_at < int(time.time()):
            self.records.pop(key, None)
            return None
        return record

    def set(self, key: str, record: OTPRecord) -> None:
        self.records[key] = record

    def delete(self, key: str) -> None:
        self.records.pop(key, None)

    def cleanup(self) -> None:
        now = int(time.time())
        expired_keys = [key for key, value in self.records.items() if value.expires_at < now]
        for key in expired_keys:
            self.records.pop(key, None)


store = OTPStore()