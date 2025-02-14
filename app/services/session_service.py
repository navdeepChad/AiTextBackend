__all__ = ["SessionService", "UserSessionInfo"]

from typing import Any, Dict
from fastapi import HTTPException
from app.models.session import UserSessionInfo

# In-memory session store
session_store: Dict[str, Dict[str, Any]] = {}


class SessionService:
    @staticmethod
    def create_session(user_info: UserSessionInfo) -> str:
        session_store[user_info.session_id] = user_info.dict()
        return user_info.session_id

    @staticmethod
    def get_session(session_id: str) -> UserSessionInfo:
        print(f"Looking for session_id: {session_id}")
        print(f"Current session_store: {session_store}")
        session_data = session_store.get(session_id)
        if not session_data:
            raise HTTPException(status_code=401, detail="Session expired or invalid")
        return UserSessionInfo(**session_data)

    @staticmethod
    def delete_session(session_id: str) -> None:
        """Delete a session from the store."""
        if session_id in session_store:
            session_store.pop(session_id)
            print(f"Session {session_id} deleted.")
        else:
            raise HTTPException(status_code=401, detail="Invalid or expired session ID")
