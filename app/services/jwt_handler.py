import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from typing import Dict, Any
from app.config_base import SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_TIME


class JWTHandler:
    @staticmethod
    def generate_jwt(payload: Dict[str, Any]) -> str:
        payload["exp"] = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_TIME)
        token: str = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token

    @staticmethod
    def verify_jwt(token: str) -> Dict[str, Any]:
        try:
            decoded_payload: Dict[str, Any] = jwt.decode(
                token, SECRET_KEY, algorithms=[JWT_ALGORITHM]
            )
            return decoded_payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
