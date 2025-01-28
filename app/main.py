from fastapi import FastAPI
from app.routers.auth_router import router as auth_router
from app.middleware.session_middleware import session_middleware
from app.config.logging_config import LOGGING_CONFIG 
import logging

app = FastAPI()
logger = logging.getLogger(__name__)
app.middleware("http")(session_middleware)
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# uvicorn app.main:app --reload
