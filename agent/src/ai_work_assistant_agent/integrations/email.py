from dataclasses import dataclass
from typing import Protocol

from ai_work_assistant_agent.api.schemas.todos import TodoCategory, TodoPriority
from ai_work_assistant_agent.integrations.work_items import ProviderAuth


@dataclass(frozen=True)
class EmailMessage:
    provider: str
    external_id: str
    subject: str
    sender: str
    body_preview: str
    web_url: str | None
    category: TodoCategory
    priority: TodoPriority
    recommended_action: str
    repo: str | None = None
    pipeline: str | None = None


@dataclass(frozen=True)
class DraftResponseRequest:
    message_id: str
    comment: str


@dataclass(frozen=True)
class DraftResponse:
    draft_id: str
    web_url: str | None


class EmailProvider(Protocol):
    provider_name: str

    def list_unread(self, auth: ProviderAuth, limit: int) -> list[EmailMessage]:
        ...

    def create_draft_response(
        self,
        request: DraftResponseRequest,
        auth: ProviderAuth,
    ) -> DraftResponse:
        ...
