from pydantic import BaseModel
from typing import Optional


class JWTToken(BaseModel):
    token: str


class AuthResponse(BaseModel):
    auth_scheme: str
    success: bool
    token: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str
