from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from ai_work_assistant_agent.api.app import create_app
from ai_work_assistant_agent.core.config import Settings


@pytest.fixture
def client(tmp_path) -> Iterator[TestClient]:
    settings = Settings(sqlite_path=tmp_path / "test.sqlite3")
    app = create_app(settings)
    with TestClient(app) as test_client:
        yield test_client
