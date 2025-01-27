import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from typing import Dict
from app.config_base import SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_TIME


class JWTHandler:
    @staticmethod
    def generate_jwt(payload: Dict) -> str:
        payload["exp"] = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_TIME)
        return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)

    @staticmethod
    def verify_jwt(token: str) -> Dict:
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
