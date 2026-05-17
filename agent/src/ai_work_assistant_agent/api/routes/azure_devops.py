from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

from ai_work_assistant_agent.api.dependencies import get_todo_repository
from ai_work_assistant_agent.api.schemas.todos import TodoRead
from ai_work_assistant_agent.integrations.azure_devops import AzureDevOpsProvider
from ai_work_assistant_agent.integrations.work_items import (
    ProviderAuth,
    WorkItemProgressUpdate,
    WorkItemQuery,
)
from ai_work_assistant_agent.persistence.todo_repository import TodoRepository
from ai_work_assistant_agent.services.todo_service import todo_to_read
from ai_work_assistant_agent.services.work_item_sync_service import WorkItemSyncService

router = APIRouter(prefix="/integrations/azure-devops", tags=["azure-devops"])

RepositoryDependency = Annotated[TodoRepository, Depends(get_todo_repository)]
PatHeader = Annotated[str | None, Header(alias="X-Azure-DevOps-PAT")]


class AzureDevOpsSyncRequest(BaseModel):
    organization: str = Field(min_length=1, max_length=200)
    project: str = Field(min_length=1, max_length=200)


class AzureDevOpsUpdateRequest(BaseModel):
    organization: str = Field(min_length=1, max_length=200)
    project: str = Field(min_length=1, max_length=200)
    work_item_id: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)


class AzureDevOpsSyncResponse(BaseModel):
    synced_count: int
    todos: list[TodoRead]


class AzureDevOpsUpdateResponse(BaseModel):
    updated: bool


@router.post("/sync", response_model=AzureDevOpsSyncResponse)
def sync_devops_tickets(
    payload: AzureDevOpsSyncRequest,
    repository: RepositoryDependency,
    pat: PatHeader = None,
) -> AzureDevOpsSyncResponse:
    auth = require_pat(pat)
    service = WorkItemSyncService(repository, AzureDevOpsProvider())
    try:
        todos = service.sync_assigned(
            WorkItemQuery(organization=payload.organization, project=payload.project),
            auth,
        )
    except httpx.HTTPStatusError as error:
        raise to_http_exception(error) from error
    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Azure DevOps request failed",
        ) from error

    return AzureDevOpsSyncResponse(
        synced_count=len(todos),
        todos=[todo_to_read(todo) for todo in todos],
    )


@router.post("/update-progress", response_model=AzureDevOpsUpdateResponse)
def update_devops_ticket_progress(
    payload: AzureDevOpsUpdateRequest,
    repository: RepositoryDependency,
    pat: PatHeader = None,
) -> AzureDevOpsUpdateResponse:
    auth = require_pat(pat)
    service = WorkItemSyncService(repository, AzureDevOpsProvider())
    try:
        service.update_progress(
            WorkItemProgressUpdate(
                organization=payload.organization,
                project=payload.project,
                work_item_id=payload.work_item_id,
                state=payload.state,
            ),
            auth,
        )
    except httpx.HTTPStatusError as error:
        raise to_http_exception(error) from error
    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Azure DevOps request failed",
        ) from error

    return AzureDevOpsUpdateResponse(updated=True)


def require_pat(pat: str | None) -> ProviderAuth:
    if not pat:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Azure DevOps PAT is required",
        )
    return ProviderAuth(token=pat)


def to_http_exception(error: httpx.HTTPStatusError) -> HTTPException:
    response_status = error.response.status_code
    if response_status in {401, 403}:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Azure DevOps authentication failed",
        )
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"Azure DevOps returned HTTP {response_status}",
    )
