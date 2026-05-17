from datetime import UTC, datetime
from uuid import uuid4

from ai_work_assistant_agent.api.schemas.todos import TodoStatus
from ai_work_assistant_agent.domain.todos import Todo
from ai_work_assistant_agent.integrations.email import (
    DraftResponse,
    DraftResponseRequest,
    EmailProvider,
)
from ai_work_assistant_agent.integrations.work_items import ProviderAuth
from ai_work_assistant_agent.persistence.todo_repository import TodoRepository


class EmailSyncService:
    def __init__(self, repository: TodoRepository, provider: EmailProvider) -> None:
        self.repository = repository
        self.provider = provider

    def sync_unread(self, auth: ProviderAuth, limit: int) -> list[Todo]:
        now = datetime.now(UTC)
        todos: list[Todo] = []
        for email in self.provider.list_unread(auth, limit):
            description = build_description(
                email.body_preview,
                email.recommended_action,
                email.repo,
                email.pipeline,
            )
            todo = Todo(
                id=str(uuid4()),
                title=f"Email: {email.subject}",
                description=description,
                status=TodoStatus.pending,
                priority=email.priority,
                source="outlook",
                external_provider=email.provider,
                external_id=email.external_id,
                external_url=email.web_url,
                category=email.category,
                created_at=now,
                updated_at=now,
            )
            todos.append(self.repository.upsert_external(todo))
        return todos

    def create_draft_response(
        self,
        request: DraftResponseRequest,
        auth: ProviderAuth,
    ) -> DraftResponse:
        return self.provider.create_draft_response(request, auth)


def build_description(
    body_preview: str,
    recommended_action: str,
    repo: str | None,
    pipeline: str | None,
) -> str:
    lines = [body_preview.strip(), "", f"Recommended next action: {recommended_action}"]
    if repo:
        lines.append(f"Repo: {repo}")
    if pipeline:
        lines.append(f"Pipeline: {pipeline}")
    return "\n".join(line for line in lines if line is not None).strip()
