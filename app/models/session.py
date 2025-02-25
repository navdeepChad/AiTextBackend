from datetime import datetime, timedelta
from pydantic import BaseModel


class UserSessionInfo(BaseModel):
    session_id: str
    public_username: str
    created_at: datetime
    expiry_time: datetime
    role: str

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expiry_time
