import logging
from typing import Any, Dict
from fastapi import HTTPException
from app.models.session import UserSessionInfo
from datetime import datetime, timedelta, timezone
from app.error.py_error import ShipotleError, BaseResponse

# In-memory session store
session_store: Dict[str, Dict[str, Any]] = {}

logger = logging.getLogger("session_service")


class SessionService:
    @staticmethod
    def create_session(user_info: UserSessionInfo) -> str:
        try:
            user_info.expiry_time = (
                datetime.now(timezone.utc).replace(tzinfo=None)
            ) + timedelta(hours=1)
            session_store[user_info.session_id] = user_info.dict()
            logger.info(
                f"Created session for user: {user_info.user_id}, session_id: {user_info.session_id}"
            )
            return user_info.session_id
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            raise ShipotleError(
                BaseResponse(
                    api_response_code=ShipotleError.INTERNAL_ERROR,
                    message="Failed to create user session",
                )
            )

    @staticmethod
    def get_session(session_id: str) -> UserSessionInfo:
        session_data = session_store.get(session_id)
        if not session_data:
            logger.warning(f"Session not found for session_id: {session_id}")
            raise ShipotleError(
                BaseResponse(
                    api_response_code=ShipotleError.AUTHORIZATION,
                    message="Session invalid",
                )
            )

        session = UserSessionInfo(**session_data)
        if session.is_expired():
            logger.warning(
                f"Session expired for user: {session.user_id}, session_id: {session_id}"
            )
            raise ShipotleError(
                BaseResponse(
                    api_response_code=ShipotleError.AUTHORIZATION,
                    message="Session expired",
                )
            )

        logger.info(
            f"Session retrieved for user: {session.user_id}, session_id: {session_id}"
        )
        return session

    @staticmethod
    def delete_session(session_id: str):
        if session_id in session_store:
            session_store.pop(session_id)
            logger.info(f"Deleted session for session_id: {session_id}")
        else:
            logger.warning(f"Attempted to delete non-existent session_id: {session_id}")
            raise ShipotleError(
                BaseResponse(
                    api_response_code=ShipotleError.AUTHORIZATION,
                    message="Invalid or expired session ID",
                )
            )
