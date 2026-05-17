from fastapi import Request

from ai_work_assistant_agent.persistence.database import Database
from ai_work_assistant_agent.persistence.todo_repository import TodoRepository
from ai_work_assistant_agent.services.todo_service import TodoService


def get_database(request: Request) -> Database:
    return request.app.state.database


def get_todo_service(request: Request) -> TodoService:
    database = get_database(request)
    repository = TodoRepository(database)
    return TodoService(repository)
