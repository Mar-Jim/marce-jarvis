import sqlite3
from pathlib import Path


class Database:
    def __init__(self, sqlite_path: Path) -> None:
        self.sqlite_path = sqlite_path

    def connect(self) -> sqlite3.Connection:
        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.sqlite_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS todos (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    source TEXT NOT NULL,
                    external_provider TEXT,
                    external_id TEXT,
                    external_url TEXT,
                    category TEXT NOT NULL DEFAULT 'normal',
                    due_at TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(external_provider, external_id)
                )
                """
            )
            self._add_column_if_missing(connection, "todos", "external_provider", "TEXT")
            self._add_column_if_missing(connection, "todos", "external_id", "TEXT")
            self._add_column_if_missing(connection, "todos", "external_url", "TEXT")
            self._add_column_if_missing(
                connection,
                "todos",
                "category",
                "TEXT NOT NULL DEFAULT 'normal'",
            )
            self._add_column_if_missing(connection, "todos", "due_at", "TEXT")
            connection.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_todos_external_ref
                ON todos(external_provider, external_id)
                WHERE external_provider IS NOT NULL AND external_id IS NOT NULL
                """
            )

    def _add_column_if_missing(
        self,
        connection: sqlite3.Connection,
        table_name: str,
        column_name: str,
        column_definition: str,
    ) -> None:
        columns = {
            row["name"]
            for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()
        }
        if column_name not in columns:
            connection.execute(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
            )
