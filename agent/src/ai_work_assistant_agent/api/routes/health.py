from typing import Literal

from fastapi import APIRouter, Request
from pydantic import BaseModel

from ai_work_assistant_agent.core.config import Settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: Literal["ok"]
    version: str


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    settings: Settings = request.app.state.settings
    return HealthResponse(status="ok", version=settings.app_version)
