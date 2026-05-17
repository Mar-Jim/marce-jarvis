from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from ai_work_assistant_agent.api.routes import azure_devops, chat, health, todos
from ai_work_assistant_agent.core.config import Settings, get_settings
from ai_work_assistant_agent.core.logging import configure_logging
from ai_work_assistant_agent.persistence.database import Database


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    configure_logging(app_settings.log_level)

    database = Database(app_settings.sqlite_path)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        database.initialize()
        yield

    app = FastAPI(
        title="AI Work Assistant Agent",
        version=app_settings.app_version,
        lifespan=lifespan,
    )
    app.state.settings = app_settings
    app.state.database = database

    app.include_router(health.router)
    app.include_router(todos.router)
    app.include_router(azure_devops.router)
    app.include_router(chat.router)

    return app
