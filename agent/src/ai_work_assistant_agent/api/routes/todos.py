from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from ai_work_assistant_agent.api.dependencies import get_todo_service
from ai_work_assistant_agent.api.schemas.todos import TodoCreate, TodoPatch, TodoRead
from ai_work_assistant_agent.services.todo_service import TodoService

router = APIRouter(prefix="/todos", tags=["todos"])

TodoServiceDependency = Annotated[TodoService, Depends(get_todo_service)]


@router.get("", response_model=list[TodoRead])
def list_todos(todo_service: TodoServiceDependency) -> list[TodoRead]:
    return todo_service.list_todos()


@router.post("", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(
    payload: TodoCreate,
    todo_service: TodoServiceDependency,
) -> TodoRead:
    return todo_service.create_todo(payload)


@router.patch("/{todo_id}", response_model=TodoRead)
def update_todo(
    todo_id: str,
    payload: TodoPatch,
    todo_service: TodoServiceDependency,
) -> TodoRead:
    todo = todo_service.update_todo(todo_id, payload)
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo
