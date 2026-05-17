from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class ChatTurnRequest(BaseModel):
    message: str
    source: Literal["vscode"]


class ChatTurnResponse(BaseModel):
    message: str


@router.post("/turn", response_model=ChatTurnResponse)
def chat_turn(_request: ChatTurnRequest) -> ChatTurnResponse:
    return ChatTurnResponse(message="Backend chat orchestration is not implemented yet.")
