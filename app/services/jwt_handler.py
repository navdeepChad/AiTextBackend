import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from typing import Dict, Any
from dotenv import load_dotenv
import os
from app.error.py_error import ShipotleError, BaseResponse
import pytz
from app.models.session import UserSessionInfo
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_TIME = int(os.getenv("JWT_EXPIRATION_TIME", 1))


class JWTHandler:
    @staticmethod
    def generate_jwt(payload: Dict[str, Any]) -> str:
        now = datetime.utcnow().replace(tzinfo=pytz.UTC)
        payload["iat"] = now
        payload["exp"] = now + timedelta(hours=JWT_EXPIRATION_TIME)

        if not SECRET_KEY:
            raise ShipotleError(
                BaseResponse(
                    api_response_code=ShipotleError.INTERNAL_ERROR,
                    message="SECRET_KEY is not set",
                )
            )
        try:
            token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
            return token
        except Exception as e:
            raise ShipotleError(
                BaseResponse(
                    api_response_code=ShipotleError.INTERNAL_ERROR,
                    message="Error encoding JWT",
                )
            )

    @staticmethod
    def verify_jwt(token: str) -> UserSessionInfo:
        if not SECRET_KEY:
            raise ShipotleError(
                BaseResponse(
                    api_response_code=ShipotleError.INTERNAL_ERROR,
                    message="Error getting secret key",
                )
            )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])

            session_info = UserSessionInfo(
                session_id=payload.get("session_id"),
                user_id=payload.get("user_id"),
                created_at=datetime.fromtimestamp(payload["iat"], tz=pytz.UTC),
                expiry_time=datetime.fromtimestamp(payload["exp"], tz=pytz.UTC),
                role=payload.get("role"),
            )

            logger.info(f"current iemes is  {datetime.utcnow()}")
            logger.info(f"token exipre {session_info.expiry_time}")

            return session_info

        except jwt.ExpiredSignatureError:
            raise ShipotleError(
                BaseResponse(
                    api_response_code=ShipotleError.AUTHORIZATION,
                    message="Token has expired",
                )
            )
        except jwt.InvalidTokenError:
            raise ShipotleError(
                BaseResponse(
                    api_response_code=ShipotleError.AUTHORIZATION,
                    message="Invalid token",
                )
            )
        except Exception as e:
            raise ShipotleError(
                BaseResponse(
                    api_response_code=ShipotleError.BADREQUEST,
                    message="Error decoding token",
                )
            )
