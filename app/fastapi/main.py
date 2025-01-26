from fastapi import FastAPI

from app.core.config import settings
from app.fastapi.endpoints import router

app = FastAPI(
    title=settings.app_title,
    description=settings.description,
    version=settings.version,
)

app.include_router(router)
