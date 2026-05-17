import logging
from datetime import UTC, datetime
from uuid import uuid4

from ai_work_assistant_agent.api.schemas.todos import TodoCreate, TodoPatch, TodoRead
from ai_work_assistant_agent.domain.todos import Todo
from ai_work_assistant_agent.persistence.todo_repository import TodoRepository

logger = logging.getLogger(__name__)


class TodoService:
    def __init__(self, repository: TodoRepository) -> None:
        self.repository = repository

    def list_todos(self) -> list[TodoRead]:
        return [todo_to_read(todo) for todo in self.repository.list()]

    def create_todo(self, payload: TodoCreate) -> TodoRead:
        now = utc_now()
        todo = Todo(
            id=str(uuid4()),
            title=payload.title,
            description=payload.description,
            status=payload.status,
            priority=payload.priority,
            source=payload.source,
            created_at=now,
            updated_at=now,
        )
        logger.info("Creating todo", extra={"todo_id": todo.id})
        return todo_to_read(self.repository.create(todo))

    def update_todo(self, todo_id: str, payload: TodoPatch) -> TodoRead | None:
        values = payload.model_dump(exclude_none=True, exclude_unset=True)
        values["updated_at"] = utc_now()
        logger.info("Updating todo", extra={"todo_id": todo_id})
        todo = self.repository.patch(todo_id, values)
        return todo_to_read(todo) if todo is not None else None


def todo_to_read(todo: Todo) -> TodoRead:
    return TodoRead(
        id=todo.id,
        title=todo.title,
        description=todo.description,
        status=todo.status,
        priority=todo.priority,
        source=todo.source,
        created_at=todo.created_at,
        updated_at=todo.updated_at,
    )


def utc_now() -> datetime:
    return datetime.now(UTC)
