import sqlite3
from collections.abc import Mapping
from datetime import datetime

from ai_work_assistant_agent.api.schemas.todos import TodoPriority, TodoStatus
from ai_work_assistant_agent.domain.todos import Todo
from ai_work_assistant_agent.persistence.database import Database


class TodoRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def list(self) -> list[Todo]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, title, description, status, priority, source, created_at, updated_at
                FROM todos
                ORDER BY created_at DESC
                """
            ).fetchall()
        return [todo_from_row(row) for row in rows]

    def create(self, todo: Todo) -> Todo:
        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO todos (
                    id, title, description, status, priority, source, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    todo.id,
                    todo.title,
                    todo.description,
                    todo.status.value,
                    todo.priority.value,
                    todo.source,
                    todo.created_at.isoformat(),
                    todo.updated_at.isoformat(),
                ),
            )
        return todo

    def get(self, todo_id: str) -> Todo | None:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT id, title, description, status, priority, source, created_at, updated_at
                FROM todos
                WHERE id = ?
                """,
                (todo_id,),
            ).fetchone()
        return todo_from_row(row) if row is not None else None

    def patch(self, todo_id: str, values: Mapping[str, object]) -> Todo | None:
        if not values:
            return self.get(todo_id)

        assignments = [f"{key} = ?" for key in values]
        parameters = [normalize_value(value) for value in values.values()]
        parameters.append(todo_id)

        with self.database.connect() as connection:
            cursor = connection.execute(
                f"""
                UPDATE todos
                SET {", ".join(assignments)}
                WHERE id = ?
                """,
                parameters,
            )
            if cursor.rowcount == 0:
                return None

        return self.get(todo_id)


def todo_from_row(row: sqlite3.Row) -> Todo:
    return Todo(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        status=TodoStatus(row["status"]),
        priority=TodoPriority(row["priority"]),
        source=row["source"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def normalize_value(value: object) -> object:
    if isinstance(value, (TodoStatus, TodoPriority)):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    return value
