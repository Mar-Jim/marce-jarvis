from dataclasses import dataclass
from datetime import datetime

from ai_work_assistant_agent.api.schemas.todos import TodoCategory, TodoPriority, TodoStatus


@dataclass(frozen=True)
class Todo:
    id: str
    title: str
    description: str
    status: TodoStatus
    priority: TodoPriority
    source: str
    external_provider: str | None
    external_id: str | None
    external_url: str | None
    category: TodoCategory
    created_at: datetime
    updated_at: datetime
