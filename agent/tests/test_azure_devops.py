import base64
import json

import httpx
from fastapi.testclient import TestClient

from ai_work_assistant_agent.integrations.azure_devops import AzureDevOpsProvider
from ai_work_assistant_agent.integrations.work_items import (
    ProviderAuth,
    WorkItemProgressUpdate,
    WorkItemQuery,
)


def test_azure_devops_provider_lists_assigned_work_items() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/_apis/wit/wiql"):
            return httpx.Response(200, json={"workItems": [{"id": 123}]})
        if request.url.path.endswith("/_apis/wit/workitemsbatch"):
            return httpx.Response(
                200,
                json={
                    "value": [
                        {
                            "id": 123,
                            "fields": {
                                "System.Title": "Fix pipeline",
                                "System.Description": "<div>Investigate failure</div>",
                                "System.State": "Active",
                                "Microsoft.VSTS.Common.Priority": 1,
                                "System.Tags": "blocked",
                            },
                            "_links": {"html": {"href": "https://example.test/work/123"}},
                        }
                    ]
                },
            )
        return httpx.Response(404)

    provider = AzureDevOpsProvider(httpx.Client(transport=httpx.MockTransport(handler)))

    items = provider.list_assigned_work_items(
        WorkItemQuery(organization="org", project="project"),
        ProviderAuth(token="secret"),
    )

    assert len(items) == 1
    assert items[0].external_id == "123"
    assert items[0].title == "Fix pipeline"
    assert items[0].status == "in_progress"
    assert items[0].priority == "urgent"
    assert items[0].category == "blocked"
    assert requests[0].headers["authorization"] == basic_pat("secret")


def test_azure_devops_provider_updates_progress() -> None:
    captured_body: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_body.append(json.loads(request.content))
        return httpx.Response(200, json={"id": 123})

    provider = AzureDevOpsProvider(httpx.Client(transport=httpx.MockTransport(handler)))

    provider.update_progress(
        WorkItemProgressUpdate(
            organization="org",
            project="project",
            work_item_id="123",
            state="Active",
        ),
        ProviderAuth(token="secret"),
    )

    assert captured_body == [
        [{"op": "add", "path": "/fields/System.State", "value": "Active"}]
    ]


def test_sync_requires_pat(client: TestClient) -> None:
    response = client.post(
        "/integrations/azure-devops/sync",
        json={"organization": "org", "project": "project"},
    )

    assert response.status_code == 401


def basic_pat(token: str) -> str:
    encoded = base64.b64encode(f":{token}".encode()).decode("ascii")
    return f"Basic {encoded}"
