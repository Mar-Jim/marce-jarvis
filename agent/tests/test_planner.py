from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient


def test_planner_prioritizes_pipeline_failures_and_blockers(client: TestClient) -> None:
    overdue_date = (datetime.now(UTC) - timedelta(days=1)).isoformat()
    create_todo(
        client,
        title="Read team newsletter",
        priority="low",
        category="informational",
        source="outlook",
        external_provider="outlook",
        external_id="msg-info",
    )
    blocked = create_todo(
        client,
        title="Blocked data contract review",
        priority="high",
        category="blocked",
        source="azure_devops",
        external_provider="azure_devops",
        external_id="456",
    )
    pipeline = create_todo(
        client,
        title="Email: Pipeline failed: daily-load",
        description="Recommended next action: Open failed run and inspect first failing task.",
        priority="urgent",
        category="pipeline_failure",
        source="outlook",
        external_provider="outlook",
        external_id="msg-pipeline",
    )
    create_todo(
        client,
        title="Overdue documentation",
        priority="medium",
        category="normal",
        due_at=overdue_date,
    )

    response = client.get("/planner/plan")

    assert response.status_code == 200
    body = response.json()
    assert body["recommended_next_task"]["todo_id"] == pipeline["id"]
    assert body["prioritized_work"][0]["category"] == "pipeline_failure"
    assert body["prioritized_work"][1]["todo_id"] == blocked["id"]
    assert body["prioritized_work"][0]["estimated_effort"] == "30-60 min"
    assert any(
        "pipeline_failure category" in reason
        for reason in body["prioritized_work"][0]["reasons"]
    )
    assert "Recommended next task" in body["optimization_summary"]


def test_planner_suggests_ticket_updates(client: TestClient) -> None:
    created = create_todo(
        client,
        title="Implement feature",
        priority="medium",
        category="in_progress",
        status="in_progress",
        source="azure_devops",
        external_provider="azure_devops",
        external_id="789",
    )

    response = client.get("/planner/plan")

    assert response.status_code == 200
    planned = response.json()["prioritized_work"][0]
    assert planned["todo_id"] == created["id"]
    assert planned["suggested_ticket_update"] == (
        "Update ticket with current progress and next validation step."
    )


def create_todo(
    client: TestClient,
    *,
    title: str,
    priority: str,
    category: str,
    description: str = "",
    status: str = "pending",
    source: str = "manual",
    external_provider: str | None = None,
    external_id: str | None = None,
    due_at: str | None = None,
) -> dict:
    response = client.post(
        "/todos",
        json={
            "title": title,
            "description": description,
            "status": status,
            "priority": priority,
            "category": category,
            "source": source,
            "external_provider": external_provider,
            "external_id": external_id,
            "due_at": due_at,
        },
    )
    assert response.status_code == 201
    return response.json()
