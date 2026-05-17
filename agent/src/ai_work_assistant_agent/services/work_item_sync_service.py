from datetime import UTC, datetime
from uuid import uuid4

from ai_work_assistant_agent.domain.todos import Todo
from ai_work_assistant_agent.integrations.work_items import (
    ProviderAuth,
    WorkItemProgressUpdate,
    WorkItemProvider,
    WorkItemQuery,
)
from ai_work_assistant_agent.persistence.todo_repository import TodoRepository


class WorkItemSyncService:
    def __init__(
        self,
        repository: TodoRepository,
        provider: WorkItemProvider,
    ) -> None:
        self.repository = repository
        self.provider = provider

    def sync_assigned(self, query: WorkItemQuery, auth: ProviderAuth) -> list[Todo]:
        synced: list[Todo] = []
        now = datetime.now(UTC)
        for item in self.provider.list_assigned_work_items(query, auth):
            todo = Todo(
                id=str(uuid4()),
                title=item.title,
                description=item.description,
                status=item.status,
                priority=item.priority,
                source=item.source,
                external_provider=item.provider,
                external_id=item.external_id,
                external_url=item.url,
                category=item.category,
                due_at=item.due_at,
                created_at=now,
                updated_at=now,
            )
            synced.append(self.repository.upsert_external(todo))
        return synced

    def update_progress(
        self,
        update: WorkItemProgressUpdate,
        auth: ProviderAuth,
    ) -> None:
        self.provider.update_progress(update, auth)
