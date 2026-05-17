from typing import Annotated, Literal

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

from ai_work_assistant_agent.api.dependencies import get_todo_repository
from ai_work_assistant_agent.api.schemas.todos import TodoRead
from ai_work_assistant_agent.integrations.email import DraftResponseRequest
from ai_work_assistant_agent.integrations.outlook_graph import OutlookGraphProvider
from ai_work_assistant_agent.integrations.work_items import ProviderAuth
from ai_work_assistant_agent.persistence.todo_repository import TodoRepository
from ai_work_assistant_agent.services.email_sync_service import EmailSyncService
from ai_work_assistant_agent.services.todo_service import todo_to_read

router = APIRouter(prefix="/integrations/outlook", tags=["outlook"])

RepositoryDependency = Annotated[TodoRepository, Depends(get_todo_repository)]
GraphTokenHeader = Annotated[str | None, Header(alias="X-Microsoft-Graph-Token")]
ApprovalHeader = Annotated[str | None, Header(alias="X-Approval-Decision")]


class OutlookSyncRequest(BaseModel):
    limit: int = Field(default=25, ge=1, le=100)


class OutlookSyncResponse(BaseModel):
    synced_count: int
    todos: list[TodoRead]


class OutlookDraftRequest(BaseModel):
    message_id: str = Field(min_length=1, max_length=500)
    comment: str = Field(min_length=1, max_length=4000)


class OutlookDraftResponse(BaseModel):
    draft_id: str
    web_url: str | None


class ApprovalRequiredResponse(BaseModel):
    approval_required: Literal[True]
    action: str
    risk: str


@router.post("/sync-unread", response_model=OutlookSyncResponse)
def sync_unread_emails(
    payload: OutlookSyncRequest,
    repository: RepositoryDependency,
    graph_token: GraphTokenHeader = None,
) -> OutlookSyncResponse:
    auth = require_graph_token(graph_token)
    service = EmailSyncService(repository, OutlookGraphProvider())
    try:
        todos = service.sync_unread(auth, payload.limit)
    except httpx.HTTPStatusError as error:
        raise to_http_exception(error) from error
    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Microsoft Graph request failed",
        ) from error

    return OutlookSyncResponse(
        synced_count=len(todos),
        todos=[todo_to_read(todo) for todo in todos],
    )


@router.post(
    "/draft-response",
    response_model=OutlookDraftResponse | ApprovalRequiredResponse,
)
def create_draft_response(
    payload: OutlookDraftRequest,
    repository: RepositoryDependency,
    graph_token: GraphTokenHeader = None,
    approval_decision: ApprovalHeader = None,
) -> OutlookDraftResponse | ApprovalRequiredResponse:
    if approval_decision != "approved":
        return ApprovalRequiredResponse(
            approval_required=True,
            action="create_outlook_draft_response",
            risk="Creates a draft email response in Outlook. It does not send email.",
        )

    auth = require_graph_token(graph_token)
    service = EmailSyncService(repository, OutlookGraphProvider())
    try:
        draft = service.create_draft_response(
            DraftResponseRequest(message_id=payload.message_id, comment=payload.comment),
            auth,
        )
    except httpx.HTTPStatusError as error:
        raise to_http_exception(error) from error
    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Microsoft Graph request failed",
        ) from error

    return OutlookDraftResponse(draft_id=draft.draft_id, web_url=draft.web_url)


def require_graph_token(token: str | None) -> ProviderAuth:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Microsoft Graph access token is required",
        )
    return ProviderAuth(token=token)


def to_http_exception(error: httpx.HTTPStatusError) -> HTTPException:
    response_status = error.response.status_code
    if response_status in {401, 403}:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Microsoft Graph authentication failed",
        )
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"Microsoft Graph returned HTTP {response_status}",
    )
