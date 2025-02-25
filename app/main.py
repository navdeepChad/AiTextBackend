from fastapi import FastAPI, Request
from app.routers.auth_router import router as auth_router
from app.middleware.session_middleware import session_middleware
from app.config.logging_config import LOGGING_CONFIG
from fastapi.responses import JSONResponse
from app.error.py_error import PyError
import logging

app = FastAPI()
logger = logging.getLogger(__name__)


@app.exception_handler(PyError)
async def pyerror_exception_handler(request : Request, exc: PyError):
    error_mapping = exc.get_error_mapping(exc.error_response.api_response_code)
    return JSONResponse(
        status_code=error_mapping["status_code"],
        content={"detail": exc.error_response.message},
    )


app.middleware("http")(session_middleware)
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# uvicorn app.main:app --reload
