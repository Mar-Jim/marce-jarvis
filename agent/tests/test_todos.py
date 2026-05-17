from fastapi.testclient import TestClient


def test_todo_lifecycle(client: TestClient) -> None:
    create_response = client.post(
        "/todos",
        json={
            "title": "Review Databricks bundle",
            "description": "Check target variables before deploy",
            "priority": "high",
            "source": "manual",
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["id"]
    assert created["title"] == "Review Databricks bundle"
    assert created["status"] == "pending"
    assert created["priority"] == "high"
    assert created["created_at"]
    assert created["updated_at"]

    list_response = client.get("/todos")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    patch_response = client.patch(
        f"/todos/{created['id']}",
        json={
            "status": "in_progress",
            "priority": "urgent",
        },
    )

    assert patch_response.status_code == 200
    patched = patch_response.json()
    assert patched["status"] == "in_progress"
    assert patched["priority"] == "urgent"
    assert patched["updated_at"] >= created["updated_at"]


def test_patch_missing_todo_returns_404(client: TestClient) -> None:
    response = client.patch("/todos/missing", json={"status": "done"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}


def test_create_todo_requires_title(client: TestClient) -> None:
    response = client.post("/todos", json={"title": ""})

    assert response.status_code == 422
