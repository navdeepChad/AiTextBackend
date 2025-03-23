from datetime import datetime, timezone
from pydantic import BaseModel


class UserSessionInfo(BaseModel):
    session_id: str
    user_id: str
    created_at: datetime
    expiry_time: datetime
    role: str

    def is_expired(self) -> bool:
        return (datetime.now(timezone.utc).replace(tzinfo=None)) > self.expiry_time
