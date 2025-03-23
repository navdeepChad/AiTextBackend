from typing import Dict, Any, Optional, List
from app.services.session_service import SessionService, UserSessionInfo
from app.services.jwt_handler import JWTHandler
from fastapi import HTTPException
import uuid
import logging
from datetime import datetime, timedelta, timezone
import os
from passlib.context import CryptContext
import pytz
from dotenv import load_dotenv
from app.error.py_error import BaseResponse, ShipotleError


class AuthScheme:
    COOKIE = "cookie"
    JWT = "jwt"


load_dotenv()


logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# dummy in memory db
user_data = {
    "test_user": {
        "password": pwd_context.hash("password123"),
        "user_id": "123",
        "email": "test@example.com",
        "public_username": "test_user",
        "role": "Admin",
    }
}


class AuthenticationService:
    @staticmethod
    def authenticate(username: str, password: str, auth_scheme: str) -> Dict[str, Any]:
        user = user_data.get(username)
        if not user or not pwd_context.verify(password, user["password"]):
            raise ShipotleError(
                BaseResponse(
                    api_response_code=ShipotleError.AUTHORIZATION,
                    message="Invalid credentials",
                )
            )

        expiry_time = (datetime.now(timezone.utc).replace(tzinfo=None)) + timedelta(
            hours=1
        )
        user_info = UserSessionInfo(
            session_id=str(uuid.uuid4()),
            role=user["role"],
            user_id=user["user_id"],
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
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
                raise ShipotleError(
                    BaseResponse(
                        api_response_code=ShipotleError.INTERNAL_ERROR,
                        message="Failed to create session",
                    )
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
                    "expires_in": int(
                        os.getenv("JWT_EXPIRATION_TIME", 1)
                    ),  # currently set to 1 day
                }
            except Exception as e:
                logger.error(f"Error generating JWT for user '{username}': {str(e)}")
                raise ShipotleError(
                    BaseResponse(
                        api_response_code=ShipotleError.INTERNAL_ERROR,
                        message="Failed to generate JWT token",
                    )
                )

        else:
            logger.error(
                f"Invalid authentication scheme provided for user '{username}': {auth_scheme}"
            )
            raise ShipotleError(
                BaseResponse(
                    api_response_code=ShipotleError.BADREQUEST,
                    message="Invalid authentication scheme",
                )
            )

    def has_required_roles(self, user_role: str, required_roles: List[str]) -> bool:
        return user_role in required_roles

    async def authenticate_async(
        self,
        auth_scheme: str,
        token: Optional[str] = None,
        session_id: Optional[str] = None,
        required_roles: Optional[List[str]] = None,
    ) -> UserSessionInfo:
        session_info: Optional[UserSessionInfo] = None

        if auth_scheme == AuthScheme.JWT and token:
            logger.info(f"Verifying JWT token: {token}")
            try:
                session_info = JWTHandler.verify_jwt(token)
                logger.info(f"Decoded JWT: {session_info}")

                if isinstance(session_info, UserSessionInfo):
                    if required_roles and not self.has_required_roles(
                        session_info.role, required_roles
                    ):
                        raise ShipotleError(
                            BaseResponse(
                                api_response_code=ShipotleError.AUTHORIZATION,
                                message="You do not have access to this resource",
                            )
                        )

                    session_info.created_at = session_info.created_at.replace(
                        tzinfo=None
                    )
                    session_info.expiry_time = session_info.expiry_time.replace(
                        tzinfo=None
                    )
                else:
                    raise ShipotleError(
                        BaseResponse(
                            api_response_code=ShipotleError.BADREQUEST,
                            message="Invalid session information in JWT",
                        )
                    )
            except ShipotleError as e:
                raise e

        elif auth_scheme == AuthScheme.COOKIE and session_id:
            try:
                session_info = SessionService.get_session(session_id)
                if required_roles and not self.has_required_roles(
                    session_info.role, required_roles
                ):
                    raise ShipotleError(
                        BaseResponse(
                            api_response_code=ShipotleError.AUTHORIZATION,
                            message="You do not have access to this resource",
                        )
                    )
            except ShipotleError as e:
                raise e

        else:
            raise ShipotleError(
                BaseResponse(
                    api_response_code=ShipotleError.BADREQUEST,
                    message="Invalid authentication scheme or missing token or session cookie",
                )
            )

        if session_info.is_expired():
            raise ShipotleError(
                BaseResponse(
                    api_response_code=ShipotleError.AUTHORIZATION,
                    message="Session has expired",
                )
            )

        return session_info
