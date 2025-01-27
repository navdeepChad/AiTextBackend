from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str
    scheme: str

class JWTToken(BaseModel):
    token: str

class AuthResponse(BaseModel):
    auth_scheme: str
    success: bool
    session_id: Optional[str] = None
    token: Optional[str] = None
