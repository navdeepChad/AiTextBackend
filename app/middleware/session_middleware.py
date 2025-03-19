import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from app.error.py_error import ShipotleError, BaseResponse

logger = logging.getLogger("session_middleware")


async def session_middleware(request: Request, call_next):
    logger.info(f"Session middleware invoked for path {request.url.path}")

    if request.url.path in ["/", "/docs", "/openapi.json", "/redoc"]:
        return await call_next(request)

    try:
        check_required_headers(request, ["x-authscheme", "x-caller", "x-correlationid"])
        request.state.x_caller = request.headers["x-caller"]
        request.state.x_correlationid = request.headers["x-correlationid"]
        request.state.x_authscheme = request.headers["x-authscheme"]

        return await call_next(request)

    except ShipotleError as e:
        logger.error(f"middleware error {e}")
        error_mapping = ShipotleError.get_error_mapping(
            e.error_response.api_response_code
        )
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


def check_required_headers(request: Request, required_headers: list):
    missing_headers = []

    for header in required_headers:
        header_value = request.headers.get(header)
        if not header_value:
            missing_headers.append(header)

    if missing_headers:
        missing_headers_str = ", ".join(missing_headers)
        logger.warning(f"Missing headers: {missing_headers_str}")
        raise ShipotleError(
            BaseResponse(
                api_response_code=ShipotleError.BADREQUEST,
                message=f"Missing required headers: {missing_headers_str}",
            )
        )
