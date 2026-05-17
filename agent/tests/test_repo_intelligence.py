from collections.abc import Iterator

from fastapi.testclient import TestClient

from ai_work_assistant_agent.api.app import create_app
from ai_work_assistant_agent.core.config import Settings


def test_repo_context_detects_project_types(tmp_path) -> None:
    (tmp_path / "databricks.yml").write_text("bundle:\n  name: demo\n", encoding="utf-8")
    (tmp_path / "queries").mkdir()
    (tmp_path / "queries" / "orders.sql").write_text("select 1", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "job.py").write_text("print('ok')", encoding="utf-8")
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("name: ci", encoding="utf-8")

    with repo_client(tmp_path) as client:
        response = client.get("/repo/context")

    assert response.status_code == 200
    body = response.json()
    assert body["databricks_bundle"] is True
    assert body["ci_cd"] is True
    assert "databricks_asset_bundle" in body["project_types"]
    assert "python" in body["project_types"]
    assert "sql" in body["project_types"]
    assert "cicd" in body["project_types"]
    assert "databricks.yml" in body["important_files"]


def test_repo_architecture_mentions_databricks(tmp_path) -> None:
    (tmp_path / "databricks.yml").write_text("bundle:\n  name: demo\n", encoding="utf-8")

    with repo_client(tmp_path) as client:
        response = client.get("/repo/architecture")

    assert response.status_code == 200
    assert "Databricks Asset Bundle detected" in response.json()["summary"]


def test_repo_command_requires_approval(tmp_path) -> None:
    with repo_client(tmp_path) as client:
        response = client.post(
            "/repo/commands/run",
            json={"command": "pytest"},
        )

    assert response.status_code == 200
    assert response.json()["approval_required"] is True


def test_file_update_requires_approval_and_stays_in_repo(tmp_path) -> None:
    with repo_client(tmp_path) as client:
        response = client.post(
            "/repo/files/update",
            json={"relative_path": "README.md", "content": "updated"},
        )
        approved = client.post(
            "/repo/files/update",
            headers={"X-Approval-Decision": "approved"},
            json={"relative_path": "README.md", "content": "updated"},
        )
        escape = client.post(
            "/repo/files/update",
            headers={"X-Approval-Decision": "approved"},
            json={"relative_path": "../escape.txt", "content": "bad"},
        )

    assert response.status_code == 200
    assert response.json()["approval_required"] is True
    assert approved.status_code == 200
    assert (tmp_path / "README.md").read_text(encoding="utf-8") == "updated"
    assert escape.status_code == 400


def repo_client(repo_root) -> Iterator[TestClient]:
    settings = Settings(sqlite_path=repo_root / "test.sqlite3", repo_root=repo_root)
    app = create_app(settings)
    return TestClient(app)
