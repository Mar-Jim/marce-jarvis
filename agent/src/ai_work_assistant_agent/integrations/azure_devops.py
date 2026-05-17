import base64
import html
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from ai_work_assistant_agent.api.schemas.todos import TodoCategory, TodoPriority, TodoStatus
from ai_work_assistant_agent.integrations.work_items import (
    ProviderAuth,
    WorkItem,
    WorkItemProgressUpdate,
    WorkItemProvider,
    WorkItemQuery,
)


class AzureDevOpsProvider(WorkItemProvider):
    provider_name = "azure_devops"

    def __init__(self, http_client: httpx.Client | None = None) -> None:
        self.http_client = http_client or httpx.Client(timeout=20)

    def list_assigned_work_items(
        self,
        query: WorkItemQuery,
        auth: ProviderAuth,
    ) -> list[WorkItem]:
        wiql_response = self.http_client.post(
            self._url(query.organization, query.project, "_apis/wit/wiql"),
            headers=self._headers(auth),
            json={
                "query": """
                    SELECT [System.Id]
                    FROM WorkItems
                    WHERE [System.AssignedTo] = @Me
                    AND [System.State] <> 'Closed'
                    AND [System.State] <> 'Removed'
                    ORDER BY [Microsoft.VSTS.Common.Priority] ASC,
                             [Microsoft.VSTS.Scheduling.DueDate] ASC
                """,
            },
        )
        wiql_response.raise_for_status()
        ids = [item["id"] for item in wiql_response.json().get("workItems", [])]
        if not ids:
            return []

        batch_response = self.http_client.post(
            self._url(query.organization, query.project, "_apis/wit/workitemsbatch"),
            headers=self._headers(auth),
            json={
                "ids": ids,
                "fields": [
                    "System.Id",
                    "System.Title",
                    "System.Description",
                    "System.State",
                    "System.WorkItemType",
                    "Microsoft.VSTS.Common.Priority",
                    "Microsoft.VSTS.Common.Severity",
                    "Microsoft.VSTS.Scheduling.DueDate",
                    "System.Tags",
                ],
            },
        )
        batch_response.raise_for_status()
        return [
            self._to_work_item(query, raw_item)
            for raw_item in batch_response.json().get("value", [])
        ]

    def update_progress(
        self,
        update: WorkItemProgressUpdate,
        auth: ProviderAuth,
    ) -> None:
        response = self.http_client.patch(
            self._url(
                update.organization,
                update.project,
                f"_apis/wit/workitems/{update.work_item_id}",
            ),
            headers={
                **self._headers(auth),
                "content-type": "application/json-patch+json",
            },
            json=[
                {
                    "op": "add",
                    "path": "/fields/System.State",
                    "value": update.state,
                }
            ],
        )
        response.raise_for_status()

    def _to_work_item(self, query: WorkItemQuery, raw_item: dict[str, Any]) -> WorkItem:
        fields = raw_item.get("fields", {})
        state = str(fields.get("System.State", ""))
        priority_value = fields.get("Microsoft.VSTS.Common.Priority")
        due_at = parse_datetime(fields.get("Microsoft.VSTS.Scheduling.DueDate"))
        tags = str(fields.get("System.Tags", ""))

        return WorkItem(
            provider=self.provider_name,
            external_id=str(raw_item["id"]),
            title=str(fields.get("System.Title", f"Work item {raw_item['id']}")),
            description=strip_html(str(fields.get("System.Description", ""))),
            status=map_state_to_todo_status(state),
            priority=map_priority(priority_value, tags),
            source="azure_devops",
            url=raw_item.get("_links", {}).get("html", {}).get("href")
            or f"https://dev.azure.com/{query.organization}/{query.project}/_workitems/edit/{raw_item['id']}",
            category=categorize(state, priority_value, due_at, tags),
            due_at=due_at,
        )

    def _url(self, organization: str, project: str, path: str) -> str:
        return f"https://dev.azure.com/{organization}/{project}/{path}?api-version=7.1"

    def _headers(self, auth: ProviderAuth) -> dict[str, str]:
        token = base64.b64encode(f":{auth.token}".encode()).decode("ascii")
        return {
            "authorization": f"Basic {token}",
            "accept": "application/json",
        }


def map_state_to_todo_status(state: str) -> TodoStatus:
    normalized = state.strip().lower()
    if normalized in {"active", "committed", "doing", "in progress", "in_progress"}:
        return TodoStatus.in_progress
    if normalized in {"done", "closed", "resolved"}:
        return TodoStatus.done
    if normalized in {"removed", "canceled", "cancelled"}:
        return TodoStatus.canceled
    return TodoStatus.pending


def map_priority(priority: object, tags: str) -> TodoPriority:
    normalized_tags = tags.lower()
    if "urgent" in normalized_tags:
        return TodoPriority.urgent
    try:
        numeric_priority = int(str(priority))
    except (TypeError, ValueError):
        return TodoPriority.medium
    if numeric_priority <= 1:
        return TodoPriority.urgent
    if numeric_priority == 2:
        return TodoPriority.high
    if numeric_priority == 3:
        return TodoPriority.medium
    return TodoPriority.low


def categorize(
    state: str,
    priority: object,
    due_at: datetime | None,
    tags: str,
) -> TodoCategory:
    normalized = f"{state} {tags}".lower()
    if "blocked" in normalized or "blocker" in normalized:
        return TodoCategory.blocked
    if map_priority(priority, tags) == TodoPriority.urgent:
        return TodoCategory.urgent
    if due_at is not None and due_at <= datetime.now(UTC) + timedelta(days=2):
        return TodoCategory.due_soon
    if map_state_to_todo_status(state) == TodoStatus.in_progress:
        return TodoCategory.in_progress
    return TodoCategory.normal


def parse_datetime(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def strip_html(value: str) -> str:
    text = html.unescape(value)
    output = []
    in_tag = False
    for char in text:
        if char == "<":
            in_tag = True
            continue
        if char == ">":
            in_tag = False
            continue
        if not in_tag:
            output.append(char)
    return "".join(output).strip()
