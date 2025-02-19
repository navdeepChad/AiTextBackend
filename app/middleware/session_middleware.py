import logging
from fastapi import Request, HTTPException
from typing import Callable, Awaitable
from fastapi import Request, HTTPException, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("session_middleware")


async def session_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    logger.info("Session middleware invoked")
    # checking the headers
    if request.url.path in ["/", "/docs", "/openapi.json", "/redoc"]:  # inital call
        return await call_next(request)
    required_headers = ["x-caller", "x-correlationid", "x-authscheme"]
    missing_headers = [
        header for header in required_headers if header not in request.headers
    ]
    if missing_headers:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required headers: {', '.join(missing_headers)}",
        )
    logger.debug(
        f"Headers received - x-caller: {request.headers.get('x-caller')}, "
        f"x-correlationid: {request.headers.get('x-correlationid')}, "
        f"x-authscheme: {request.headers.get('x-authscheme')}"
    )
    request.state.x_caller = request.headers["x-caller"]
    request.state.x_correlationid = request.headers["x-correlationid"]
    request.state.x_authscheme = request.headers["x-authscheme"]

    response = await call_next(request)
    return response
