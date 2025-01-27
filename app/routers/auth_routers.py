import logging
from fastapi import APIRouter, Response, Depends, Request, HTTPException, Form
from app.services.auth_service import AuthenticationService, AuthScheme
from app.services.jwt_handler import JWTHandler
from app.services.session_service import SessionService

router = APIRouter()
logger = logging.getLogger("auth_router")

@router.post("/login")
def login(
    response: Response,
    request: Request,
    username: str = Form(...),  
    password: str = Form(...),
):
    logger.info("Login endpoint hit")
    x_caller = request.headers.get("x-caller")
    x_correlationid = request.headers.get("x-correlationid")
    x_authscheme = request.headers.get("x-authscheme")

    if not x_caller or not x_correlationid or not x_authscheme:
        raise HTTPException(status_code=400, detail="Missing required headers")

    try:
        auth_response = AuthenticationService.authenticate(
            username=username,
            password=password,
            auth_scheme=x_authscheme,  
        )
        logger.info(f"User '{username}' authenticated successfully using {x_authscheme}")
    except Exception as e:
        logger.error(f"authentication failed for user '{username}': {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")

    if x_authscheme == AuthScheme.COOKIE:
        response.set_cookie(
            key="session_id",
            value=auth_response["session_id"],
            httponly=True,
            secure=False,
        )

    return auth_response



@router.get("/protected")
def protected_route(request: Request):
    logger.info("Protected endpoint hit")
    #authoriastion
    x_authscheme = request.headers.get("x-authscheme")
    if not x_authscheme:
        raise HTTPException(status_code=400, detail="missing x-authscheme header")

    if x_authscheme == "jwt":
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            logger.warning("missing or invalid authorization header")
            raise HTTPException(status_code=401, detail="missing or invalid authorization header")
        
        token = authorization.split(" ")[1]
        try:
            user_data = JWTHandler.verify_jwt(token)
            logger.info(f"token verified successfully for user: {user_data['public_username']}")
        except Exception as e:
            logger.error(f"token verification failed: {str(e)}")
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

        return {"message": f"accesed the protected route {user_data.get('public_username')}"}

    elif x_authscheme == "cookie":
        session_id = request.cookies.get("session_id")
        if not session_id:
            logger.warning("session cookie missing")
            raise HTTPException(status_code=401, detail="session cookie missing")
        
        try:
            session=SessionService.get_session(session_id)
            logger.info(f"session verified successfully for user: {session.public_username}")
        except Exception as e:
            print(f"received session_id from cookie: {session_id}")
            logger.error(f"ssession validation failed: {str(e)}")
            raise HTTPException(status_code=401, detail=f"invalid session id: {str(e)}")

        return {"message": f"Welcome {session.public_username}"}

    else:
        raise HTTPException(status_code=400, detail="invalid x-authscheme value")

@router.post("/logout")
def logout(request: Request, response: Response):
    logger.info("Logout endpoint hit")
    x_authscheme = request.headers.get("x-authscheme")
    if not x_authscheme:
        logger.warning("missing x-authscheme header")
        raise HTTPException(status_code=400, detail="Missing x-authscheme header")

    #not implemented
    if x_authscheme == "jwt":
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            logger.warning("missing or invalid Authorization header")
            raise HTTPException(status_code=401, detail="missing or invalid Authorization header")

        token = authorization.split(" ")[1]
        logger.info(f"Logging out user with JWT token: {token}")
        return {"message": "Logged out successfully. Please discard your token client-side."}

    elif x_authscheme == "cookie":
        session_id = request.cookies.get("session_id")
        if not session_id:
            logger.warning("Session cookie missing")
            raise HTTPException(status_code=401, detail="Session cookie missing")

        try:
            SessionService.delete_session(session_id)
            response.delete_cookie(key="session_id")
            logger.info(f"session {session_id} logout")
            print(f"loogged out session_id: {session_id}")
            return {"message": "Logged out successfully"}
        except Exception as e:
            logger.error(f"Error during session logout: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error during logout: {str(e)}")

    else:
        logger.error("Invalid x-authscheme value")
        raise HTTPException(status_code=400, detail="Invalid x-authscheme value")
