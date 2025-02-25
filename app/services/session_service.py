import logging
from typing import Any, Dict
from fastapi import HTTPException
from app.models.session import UserSessionInfo
from datetime import datetime, timedelta
from typing import Optional
from app.error.py_error import PyError, BaseResponse

# In-memory session store
session_store: Dict[str, Dict[str, Any]] = {}


logger = logging.getLogger("session_service")


class SessionService:
    @staticmethod
    def create_session(user_info: UserSessionInfo) -> str:
        try:
            user_info.expiry_time = datetime.utcnow() + timedelta(hours=1)
            session_store[user_info.session_id] = user_info.dict()
            logger.info(
                f"Created session for user: {user_info.public_username}, session_id: {user_info.session_id}"
            )
            return user_info.session_id
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            raise PyError(
                BaseResponse(
                    api_response_code=PyError.INTERNAL_ERROR,
                    message="Failed to create user session",
                ),
                message=f"Unexpected error while creating session: {str(e)}",
            )

    @staticmethod
    def get_session(session_id: str) -> UserSessionInfo:
        session_data = session_store.get(session_id)
        if not session_data:
            logger.warning(f"Session not found for session_id: {session_id}")
            raise PyError(
                BaseResponse(
                    api_response_code=PyError.AUTHORIZATION, message="Session invalid"
                ),
                message="Session not found",
            )

        session = UserSessionInfo(**session_data)
        if session.is_expired():
            logger.warning(
                f"Session expired for user: {session.public_username}, session_id: {session_id}"
            )
            raise PyError(
                BaseResponse(
                    api_response_code=PyError.AUTHORIZATION, message="Session expired"
                ),
                message="User session has expired",
            )

        logger.info(
            f"Session retrieved for user: {session.public_username}, session_id: {session_id}"
        )
        return session

    @staticmethod
    def delete_session(session_id: str):
        if session_id in session_store:
            session_store.pop(session_id)
            logger.info(f"Deleted session for session_id: {session_id}")
        else:
            logger.warning(f"Attempted to delete non-existent session_id: {session_id}")
            raise PyError(
                BaseResponse(
                    api_response_code=PyError.AUTHORIZATION,
                    message="Invalid or expired session ID",
                ),
                message="Attempted to delete an invalid or already expired session",
            )
