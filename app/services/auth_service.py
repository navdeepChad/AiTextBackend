from typing import Dict, Union, Any
from app.services.session_service import SessionService, UserSessionInfo
from app.services.jwt_handler import JWTHandler
from fastapi import HTTPException
import uuid
import logging
from datetime import datetime, timedelta
from passlib.context import CryptContext
import pytz
from app.error.py_error import BaseResponse, PyError



class AuthScheme:
    COOKIE = "cookie"
    JWT = "jwt"

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# dummy in memory db
user_data = {
    "test_user": {
        "password": pwd_context.hash("password123"),
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
        if not user or not pwd_context.verify(password, user["password"]):
            raise PyError(
                BaseResponse(
                    api_response_code=PyError.AUTHORIZATION,
                    message="Invalid credentials",
                ),
                message="Invalid username or password",
            )

        expiry_time = datetime.utcnow() + timedelta(hours=1)
        user_info = UserSessionInfo(
            session_id=str(uuid.uuid4()),
            role=user["role"],
            public_username=user["public_username"],
            created_at=datetime.utcnow(),
            expiry_time=expiry_time,
        )

        if auth_scheme == AuthScheme.COOKIE:
            try:
                session_id = SessionService.create_session(user_info)
                logger.info(f"Session created for user '{username}'")
                return {
                    "auth_scheme": AuthScheme.COOKIE,
                    "success": True,
                    "session_id": session_id,
                    "expires_in": expiry_time.replace(tzinfo=pytz.UTC),
                }
            except Exception as e:
                logger.error(f"Error creating session for user '{username}': {str(e)}")
                raise PyError(
                    BaseResponse(
                        api_response_code=PyError.INTERNAL_ERROR,
                        message="Failed to create session",
                    ),
                    message=f"Error creating session for user '{username}': {str(e)}",
                )


        elif auth_scheme == AuthScheme.JWT:
            try:
                payload = user_info.dict()
                payload["created_at"] = user_info.created_at.isoformat(
                    sep=" ", timespec="seconds"
                )
                payload["expiry_time"] = user_info.expiry_time.isoformat(
                    sep=" ", timespec="seconds"
                )
                payload["sub"] = user["user_id"]
                
                token = JWTHandler.generate_jwt(payload)
                logger.info(f"JWT generated for user '{username}'")
                return {
                    "auth_scheme": AuthScheme.JWT,
                    "success": True,
                    "token": token,
                    "expires_in": "86400", # currently set to 1 day
                }
            except Exception as e:
                logger.error(f"Error generating JWT for user '{username}': {str(e)}")
                raise PyError(
                    BaseResponse(
                        api_response_code=PyError.INTERNAL_ERROR,
                        message="Failed to generate JWT token",
                    ),
                    message=f"Error generating JWT for user '{username}': {str(e)}",
                )

        else:
            logger.error(f"Invalid authentication scheme provided for user '{username}': {auth_scheme}")
            raise PyError(
                BaseResponse(
                    api_response_code=PyError.BADREQUEST,
                    message="Invalid authentication scheme",
                ),
                message="Auth scheme must be either 'cookie' or 'jwt'",
            )
