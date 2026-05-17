from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class TodoStatus(StrEnum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"
    canceled = "canceled"


class TodoPriority(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class TodoCategory(StrEnum):
    blocked = "blocked"
    in_progress = "in_progress"
    urgent = "urgent"
    due_soon = "due_soon"
    pipeline_failure = "pipeline_failure"
    needs_response = "needs_response"
    needs_action = "needs_action"
    informational = "informational"
    meeting_context = "meeting_context"
    normal = "normal"


class TodoBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=4000)
    status: TodoStatus = TodoStatus.pending
    priority: TodoPriority = TodoPriority.medium
    source: str = Field(default="manual", min_length=1, max_length=100)
    external_provider: str | None = Field(default=None, max_length=100)
    external_id: str | None = Field(default=None, max_length=100)
    external_url: str | None = Field(default=None, max_length=2000)
    category: TodoCategory = TodoCategory.normal


class TodoCreate(TodoBase):
    pass


class TodoPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=4000)
    status: TodoStatus | None = None
    priority: TodoPriority | None = None
    source: str | None = Field(default=None, min_length=1, max_length=100)
    external_provider: str | None = Field(default=None, max_length=100)
    external_id: str | None = Field(default=None, max_length=100)
    external_url: str | None = Field(default=None, max_length=2000)
    category: TodoCategory | None = None


class TodoRead(TodoBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
