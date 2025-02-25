import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from app.error.py_error import PyError, BaseResponse

logger = logging.getLogger("session_middleware")


async def session_middleware(request: Request, call_next):
    logger.info(f"Session middleware invoked for path {request.url.path}")

    if request.url.path in ["/", "/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)

    try:
        required_headers = ["x-caller", "x-correlationid", "x-authscheme"]
        missing_headers = [header for header in required_headers if header not in request.headers]

        if missing_headers:
            logger.warning(f"Missing headers: {', '.join(missing_headers)}")
            raise PyError(
                BaseResponse(
                    api_response_code=PyError.BADREQUEST,
                    message=f"Missing required headers: {', '.join(missing_headers)}", 
                ),
                message="Request is missing required headers." 
            )

        request.state.x_caller = request.headers["x-caller"]
        request.state.x_correlationid = request.headers["x-correlationid"]
        request.state.x_authscheme = request.headers["x-authscheme"]

        return await call_next(request)

    except PyError as e:
        logger.error(f"middleware error {e}")
        error_mapping = PyError.get_error_mapping(e.error_response.api_response_code)
        return JSONResponse(
            status_code=error_mapping["status_code"],
            content={"detail": e.error_response.message},
        )

    except Exception as e:
        logger.error(f"Unexpected middleware error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred in session middleware."},
        )
