from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from ai_work_assistant_agent.api.schemas.todos import TodoCategory, TodoPriority, TodoStatus


@dataclass(frozen=True)
class ProviderAuth:
    token: str


@dataclass(frozen=True)
class WorkItemQuery:
    organization: str
    project: str


@dataclass(frozen=True)
class WorkItemProgressUpdate:
    organization: str
    project: str
    work_item_id: str
    state: str


@dataclass(frozen=True)
class WorkItem:
    provider: str
    external_id: str
    title: str
    description: str
    status: TodoStatus
    priority: TodoPriority
    source: str
    url: str | None
    category: TodoCategory
    due_at: datetime | None = None


class WorkItemProvider(Protocol):
    provider_name: str

    def list_assigned_work_items(
        self,
        query: WorkItemQuery,
        auth: ProviderAuth,
    ) -> list[WorkItem]:
        ...

    def update_progress(
        self,
        update: WorkItemProgressUpdate,
        auth: ProviderAuth,
    ) -> None:
        ...
