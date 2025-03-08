import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from typing import Dict, Any
from dotenv import load_dotenv
import os
from app.error.py_error import ShipotleError, BaseResponse

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_TIME = int(os.getenv("JWT_EXPIRATION_TIME", 1))


class JWTHandler:
    @staticmethod
    def generate_jwt(payload: Dict[str, Any]) -> str:
        payload["exp"] = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_TIME)
        payload["iat"] = datetime.utcnow()
        if not SECRET_KEY:
            raise ShipotleError(
                BaseResponse(
                    api_response_code=ShipotleError.INTERNAL_ERROR,
                    message="SECRET_KEY is not set",
                ),
                message="JWT generation failed due to missing SECRET_KEY",
            )
        try:
            token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
            return token
        except Exception as e:
            raise ShipotleError(
                BaseResponse(
                    api_response_code=ShipotleError.INTERNAL_ERROR,
                    message="Error encoding JWT",
                ),
                message=f"JWT encoding error: {str(e)}",
            )

    @staticmethod
    def verify_jwt(token: str) -> Dict:
        if not SECRET_KEY:
            raise ShipotleError(
                BaseResponse(
                    api_response_code=ShipotleError.INTERNAL_ERROR,
                    message="error getting secret key",
                ),
                message="error getting secret key",
            )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise ShipotleError(
                BaseResponse(
                    api_response_code=ShipotleError.AUTHORIZATION,
                    message="token has expired",
                ),
                message="token has expired",
            )
        except jwt.InvalidTokenError:
            raise ShipotleError(
                BaseResponse(
                    api_response_code=ShipotleError.AUTHORIZATION,
                    message="Invalid token",
                ),
                message="invalid JWT token",
            )
        except Exception as e:
            raise ShipotleError(
                BaseResponse(
                    api_response_code=ShipotleError.BADREQUEST,
                    message="Error decoding token",
                ),
                message=f"JWT decoding error: {str(e)}",
            )
