import logging
from fastapi import APIRouter, Response, Request, HTTPException, Depends
from app.services.auth_service import AuthenticationService, AuthScheme
from app.models.auth import LoginRequest
from app.services.session_service import SessionService
from app.error.py_error import BaseResponse, ShipotleError
from app.middleware.session_middleware import check_required_headers
from typing import Dict, Any
from datetime import datetime, timedelta

router = APIRouter()
logger = logging.getLogger("auth_router")


@router.post("/login")
def login(
    response: Response, request: Request, login_data: LoginRequest
) -> Dict[str, Any]:
    logger.info("Login endpoint hit")
    check_required_headers(request, ["x-authscheme"])
    x_authscheme = request.headers.get("x-authscheme")

    try:
        auth_response = AuthenticationService.authenticate(
            username=login_data.username,
            password=login_data.password,
            auth_scheme=x_authscheme if x_authscheme else "",
        )
        logger.info(
            f"User '{login_data.username}' authenticated successfully using {x_authscheme}"
        )

        if x_authscheme == AuthScheme.COOKIE:
            expires = datetime.utcnow() + timedelta(hours=1)
            response.set_cookie(
                key="session_id",
                value=auth_response["session_id"],
                httponly=True,
                secure=False,
                expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            )
    except Exception as e:
        logger.error(
            f"Authentication failed for user '{login_data.username}': {str(e)}"
        )
        raise ShipotleError(
            BaseResponse(
                api_response_code=ShipotleError.AUTHORIZATION,
                message="Authentication failed",
            )
        )

    return auth_response


@router.get("/protected")
async def protected_route(request: Request) -> Dict[str, str]:
    auth_service = AuthenticationService()
    logger.info("Protected endpoint hit")
    check_required_headers(request, ["x-authscheme"])
    x_authscheme = request.headers.get("x-authscheme")

    required_roles = ["Admin"]

    try:
        token = (
            request.headers.get("Authorization", "").split(" ")[1]
            if x_authscheme == AuthScheme.JWT
            else None
        )
        session_id = (
            request.cookies.get("session_id")
            if x_authscheme == AuthScheme.COOKIE
            else None
        )

        session_info = await auth_service.authenticate_async(
            auth_scheme=x_authscheme if x_authscheme else "",
            token=token,
            session_id=session_id,
            required_roles=required_roles,
        )

        logger.info(f"Session verified successfully for user: {session_info.user_id}")
        return {"message": "Accessed the protected route"}

    except HTTPException as e:
        logger.error(f"Authentication failed: {str(e.detail)}")
        raise ShipotleError(
            BaseResponse(
                api_response_code=ShipotleError.AUTHORIZATION,
                message="Authentication failed",
            )
        )


@router.post("/logout")
def logout(request: Request, response: Response) -> Dict[str, str]:
    logger.info("Logout endpoint hit")
    check_required_headers(request, ["x-authscheme"])
    x_authscheme = request.headers.get("x-authscheme")

    try:
        if x_authscheme == AuthScheme.JWT:
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                logger.warning("Missing or invalid Authorization header")
                raise ShipotleError(
                    BaseResponse(
                        api_response_code=ShipotleError.BADREQUEST,
                        message="Missing or invalid Authorization header",
                    )
                )

            token = authorization.split(" ")[1]
            logger.info(f"Logging out user with JWT token: {token}")
            return {
                "message": "Logged out successfully. Please discard your token client-side."
            }

        elif x_authscheme == AuthScheme.COOKIE:
            session_id = request.cookies.get("session_id")
            if not session_id:
                logger.warning("Session cookie missing")
                raise ShipotleError(
                    BaseResponse(
                        api_response_code=ShipotleError.AUTHORIZATION,
                        message="Session cookie missing",
                    )
                )

            SessionService.delete_session(session_id)
            response.delete_cookie(key="session_id")
            logger.info(f"Logged out session: {session_id}")
            return {"message": "Logged out successfully"}

        else:
            logger.error("Invalid x-authscheme value")
            raise ShipotleError(
                BaseResponse(
                    api_response_code=ShipotleError.BADREQUEST,
                    message="Invalid x-authscheme value",
                )
            )
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise ShipotleError(
            BaseResponse(
                api_response_code=ShipotleError.INTERNAL_ERROR,
                message="Error during session logout",
            )
        )
