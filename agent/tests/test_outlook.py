import httpx
from fastapi.testclient import TestClient

from ai_work_assistant_agent.integrations.email import DraftResponseRequest
from ai_work_assistant_agent.integrations.outlook_graph import OutlookGraphProvider
from ai_work_assistant_agent.integrations.work_items import ProviderAuth


def test_outlook_provider_classifies_pipeline_failures() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "value": [
                    {
                        "id": "msg-1",
                        "subject": "Pipeline failed: daily-load #42",
                        "bodyPreview": (
                            "Repository: data/platform Pipeline: daily-load failed at tests"
                        ),
                        "from": {"emailAddress": {"address": "ado@example.com"}},
                        "webLink": "https://outlook.example/message/msg-1",
                    }
                ]
            },
        )

    provider = OutlookGraphProvider(httpx.Client(transport=httpx.MockTransport(handler)))

    messages = provider.list_unread(ProviderAuth(token="graph-token"), limit=10)

    assert len(messages) == 1
    assert messages[0].category == "pipeline_failure"
    assert messages[0].priority == "urgent"
    assert messages[0].repo == "data/platform"
    assert messages[0].pipeline == "daily-load"
    assert "first failing task" in messages[0].recommended_action
    assert requests[0].headers["authorization"] == "Bearer graph-token"


def test_outlook_provider_creates_draft_response() -> None:
    captured_body: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_body.append(request.read())
        return httpx.Response(
            201,
            json={"id": "draft-1", "webLink": "https://outlook.example/drafts/draft-1"},
        )

    provider = OutlookGraphProvider(httpx.Client(transport=httpx.MockTransport(handler)))

    draft = provider.create_draft_response(
        request=DraftResponseRequest(message_id="msg-1", comment="Thanks, I will review."),
        auth=ProviderAuth(token="graph-token"),
    )

    assert draft.draft_id == "draft-1"
    assert draft.web_url == "https://outlook.example/drafts/draft-1"
    assert captured_body


def test_outlook_sync_requires_graph_token(client: TestClient) -> None:
    response = client.post("/integrations/outlook/sync-unread", json={"limit": 10})

    assert response.status_code == 401


def test_outlook_draft_requires_approval_before_outbound_action(client: TestClient) -> None:
    response = client.post(
        "/integrations/outlook/draft-response",
        headers={"X-Microsoft-Graph-Token": "token"},
        json={"message_id": "msg-1", "comment": "Thanks"},
    )

    assert response.status_code == 200
    assert response.json()["approval_required"] is True
