from typing import Dict, Union, Any
from app.services.session_service import SessionService, UserSessionInfo
from app.services.jwt_handler import JWTHandler
from fastapi import HTTPException
import uuid


class AuthScheme:
    COOKIE = "cookie"
    JWT = "jwt"


# dummy in memory db
user_data = {
    "test_user": {
        "password": "password123",
        "user_id": "123",
        "email": "test@example.com",
        "public_username": "test_user",
        "role": "admin",
    }
}


class AuthenticationService:
    @staticmethod
    def authenticate(username: str, password: str, auth_scheme: str) -> Dict[str, Any]:
        user = user_data.get(username)
        if not user or user["password"] != password:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_info = UserSessionInfo(
            session_id=str(uuid.uuid4()),
            user_id=user["user_id"],
            email=user["email"],
            public_username=user["public_username"],
            role=user["role"],
        )

        if auth_scheme == AuthScheme.COOKIE:
            SessionService.create_session(user_info)
            return {
                "auth_scheme": AuthScheme.COOKIE,
                "success": True,
                "session_id": user_info.session_id,
            }

        elif auth_scheme == AuthScheme.JWT:
            token = JWTHandler.generate_jwt(user_info.dict())
            return {"auth_scheme": AuthScheme.JWT, "success": True, "token": token}

        else:
            raise HTTPException(status_code=400, detail="Invalid authentication scheme")
