from pydantic import BaseModel

class UserSessionInfo(BaseModel):
    session_id: str
    user_id: str
    email: str
    public_username: str
    role: str
