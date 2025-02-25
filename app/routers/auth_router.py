import logging
from fastapi import APIRouter, Response, Depends, Request, HTTPException, Form
from app.services.auth_service import AuthenticationService, AuthScheme
from app.services.jwt_handler import JWTHandler
from app.services.session_service import SessionService
from datetime import datetime, timedelta
from app.error.py_error import BaseResponse, PyError
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

router = APIRouter()
logger = logging.getLogger("auth_router")


@router.post("/login")
def login(
    response: Response,
    request: Request,
    username: str = Form(...), 
    password: str = Form(...),
) -> Dict[str, Any]:
    logger.info("Login endpoint hit")
    x_caller = request.headers.get("x-caller")
    x_correlationid = request.headers.get("x-correlationid")
    x_authscheme = request.headers.get("x-authscheme")

    try:
        auth_response = AuthenticationService.authenticate(
            username=username,
            password=password,
            auth_scheme=x_authscheme if x_authscheme else "",
        )
        logger.info(
            f"User '{username}' authenticated successfully using {x_authscheme}"
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
        logger.error(f"Authentication failed for user '{username}': {str(e)}")
        raise PyError(
            BaseResponse(
                api_response_code=PyError.AUTHORIZATION, message="Authentication failed"
            ),
            message=f"Authentication failed for user '{username}': {str(e)}",
        )

    return auth_response


@router.get("/protected")
def protected_route(request: Request) -> Dict[str, str]:
    logger.info("Protected endpoint hit")
    x_authscheme = request.headers.get("x-authscheme")
    if not x_authscheme:
        logger.warning("Missing x-authscheme header")
        raise PyError(
            BaseResponse(
                api_response_code=PyError.AUTHORIZATION,
                message="Missing x-authscheme header",
            ),
            message="x-authscheme header is missing",
        )

    if x_authscheme == "jwt":
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            logger.warning("Missing or invalid Authorization header")
            raise PyError(
                BaseResponse(
                    api_response_code=PyError.AUTHORIZATION,
                    message="Missing or invalid Authorization header",
                ),
                message="Missing or invalid Authorization header",
            )

        token = authorization.split(" ")[1]
        try:
            user_data = JWTHandler.verify_jwt(token)
            logger.info(f"Token verified successfully for user: {user_data['sub']}")
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise PyError(
                BaseResponse(
                    api_response_code=PyError.AUTHORIZATION, message="Invalid token"
                ),
                message=f"Token verification failed: {str(e)}",
            )

        return {"message": f"Accessed the protected route via JWT"}

    elif x_authscheme == "cookie":
        session_id = request.cookies.get("session_id")
        if not session_id:
            logger.warning("Session cookie missing")
            raise PyError(
                BaseResponse(
                    api_response_code=PyError.AUTHORIZATION,
                    message="Session cookie missing",
                ),
                message="Session cookie missing",
            )

        try:
            session = SessionService.get_session(session_id)
            logger.info(
                f"Session verified successfully for user: {session.public_username}"
            )
        except Exception as e:
            logger.error(f"Session validation failed: {str(e)}")
            raise PyError(
                BaseResponse(
                    api_response_code=PyError.AUTHORIZATION, message="Invalid session"
                ),
                message=f"Session validation failed: {str(e)}",
            )

        return {"message": f"Accessed the protected route via Cookie"}

    else:
        logger.error("Invalid x-authscheme value")
        raise PyError(
            BaseResponse(
                api_response_code=PyError.AUTHORIZATION,
                message="Invalid x-authscheme value",
            ),
            message="Invalid x-authscheme value",
        )



@router.post("/logout")
def logout(request: Request, response: Response) -> Dict[str, str]:
    logger.info("Logout endpoint hit")
    x_authscheme = request.headers.get("x-authscheme")
    if not x_authscheme:
        logger.warning("Missing x-authscheme header")
        raise PyError(
            BaseResponse(
                api_response_code=PyError.BADREQUEST,
                message="Missing x-authscheme header",
            ),
            message="Missing x-authscheme header",
        )

    if x_authscheme == "jwt":
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            logger.warning("Missing or invalid Authorization header")
            raise PyError(
                BaseResponse(
                    api_response_code=PyError.BADREQUEST,
                    message="Missing or invalid Authorization header",
                ),
                message="Missing or invalid Authorization header",
            )

        token = authorization.split(" ")[1]
        logger.info(f"Logging out user with JWT token: {token}")
        return {
            "message": "Logged out successfully. Please discard your token client-side."
        }

    elif x_authscheme == "cookie":
        session_id = request.cookies.get("session_id")
        if not session_id:
            logger.warning("Session cookie missing")
            raise PyError(
                BaseResponse(
                    api_response_code=PyError.AUTHORIZATION,
                    message="Session cookie missing",
                ),
                message="Session cookie missing",
            )

        try:
            SessionService.delete_session(session_id)
            response.delete_cookie(key="session_id")
            logger.info(f"Logged out session: {session_id}")
            return {"message": "Logged out successfully"}
        except HTTPException as e:
            logger.error(f"Error during session logout: {str(e)}")
            raise PyError(
                BaseResponse(
                    api_response_code=PyError.INTERNAL_ERROR,
                    message="Error during session logout",
                ),
                message=f"Error during session logout: {str(e)}",
            )

    else:
        logger.error("Invalid x-authscheme value")
        raise PyError(
            BaseResponse(
                api_response_code=PyError.BADREQUEST,
                message="Invalid x-authscheme value",
            ),
            message="Invalid x-authscheme value",
        )
