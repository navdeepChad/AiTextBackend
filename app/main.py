from fastapi import FastAPI, Request
from app.routers.auth_router import router as auth_router
from app.middleware.session_middleware import session_middleware
from app.config.logging_config import LOGGING_CONFIG
from fastapi.responses import JSONResponse
from app.error.py_error import ShipotleError
import logging

app = FastAPI()
logger = logging.getLogger(__name__)


@app.exception_handler(ShipotleError)
async def pyerror_exception_handler(request: Request, exc: ShipotleError):
    response_body = exc.to_action_result()
    return JSONResponse(
        status_code=response_body["status_code"],
        content=response_body,
    )


app.middleware("http")(session_middleware)
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# uvicorn app.main:app --reload
