from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AI Work Assistant Agent", version="0.1.0")


class HealthResponse(BaseModel):
    status: Literal["ok"]
    version: str


class ChatTurnRequest(BaseModel):
    message: str
    source: Literal["vscode"]


class ChatTurnResponse(BaseModel):
    message: str


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version="0.1.0")


@app.post("/api/v1/chat/turn", response_model=ChatTurnResponse)
def chat_turn(_request: ChatTurnRequest) -> ChatTurnResponse:
    return ChatTurnResponse(
        message="Backend chat orchestration is not implemented yet.",
    )
