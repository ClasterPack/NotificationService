from fastapi import FastAPI

from api.v1 import notifications
from core.config import settings
from core.logger import logger

app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
)
app.include_router(notifications.router)

logger.info("приложение запущено")
