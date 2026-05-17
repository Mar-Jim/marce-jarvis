import re
from typing import Any

import httpx

from ai_work_assistant_agent.api.schemas.todos import TodoCategory, TodoPriority
from ai_work_assistant_agent.integrations.email import (
    DraftResponse,
    DraftResponseRequest,
    EmailMessage,
)
from ai_work_assistant_agent.integrations.work_items import ProviderAuth


class OutlookGraphProvider:
    provider_name = "outlook"

    def __init__(self, http_client: httpx.Client | None = None) -> None:
        self.http_client = http_client or httpx.Client(timeout=20)

    def list_unread(self, auth: ProviderAuth, limit: int) -> list[EmailMessage]:
        response = self.http_client.get(
            "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages",
            headers=self._headers(auth),
            params={
                "$filter": "isRead eq false",
                "$top": str(limit),
                "$select": "id,subject,bodyPreview,from,receivedDateTime,webLink,importance",
                "$orderby": "receivedDateTime desc",
            },
        )
        response.raise_for_status()
        return [self._to_email_message(raw) for raw in response.json().get("value", [])]

    def create_draft_response(
        self,
        request: DraftResponseRequest,
        auth: ProviderAuth,
    ) -> DraftResponse:
        response = self.http_client.post(
            f"https://graph.microsoft.com/v1.0/me/messages/{request.message_id}/createReply",
            headers=self._headers(auth),
            json={"comment": request.comment},
        )
        response.raise_for_status()
        data = response.json()
        return DraftResponse(draft_id=str(data.get("id", "")), web_url=data.get("webLink"))

    def _to_email_message(self, raw: dict[str, Any]) -> EmailMessage:
        subject = str(raw.get("subject") or "(no subject)")
        body_preview = str(raw.get("bodyPreview") or "")
        sender = (
            raw.get("from", {})
            .get("emailAddress", {})
            .get("address", "unknown sender")
        )
        category = classify_email(subject, body_preview)
        repo = identify_repo(subject, body_preview)
        pipeline = identify_pipeline(subject, body_preview)
        return EmailMessage(
            provider=self.provider_name,
            external_id=str(raw["id"]),
            subject=subject,
            sender=str(sender),
            body_preview=body_preview,
            web_url=raw.get("webLink"),
            category=category,
            priority=(
                TodoPriority.urgent
                if category == TodoCategory.pipeline_failure
                else priority_for(category)
            ),
            recommended_action=recommend_action(category, repo, pipeline),
            repo=repo,
            pipeline=pipeline,
        )

    def _headers(self, auth: ProviderAuth) -> dict[str, str]:
        return {
            "authorization": f"Bearer {auth.token}",
            "accept": "application/json",
        }


def classify_email(subject: str, body_preview: str) -> TodoCategory:
    text = f"{subject} {body_preview}".lower()
    pipeline_terms = ["pipeline failed", "build failed", "release failed", "deployment failed"]
    if any(term in text for term in pipeline_terms):
        return TodoCategory.pipeline_failure
    response_terms = ["please respond", "can you reply", "waiting for your response"]
    if any(term in text for term in response_terms):
        return TodoCategory.needs_response
    action_terms = ["action required", "please review", "approval required", "todo"]
    if any(term in text for term in action_terms):
        return TodoCategory.needs_action
    if any(term in text for term in ["meeting", "agenda", "follow-up", "recap"]):
        return TodoCategory.meeting_context
    return TodoCategory.informational


def priority_for(category: TodoCategory) -> TodoPriority:
    if category in {TodoCategory.needs_response, TodoCategory.needs_action}:
        return TodoPriority.high
    if category == TodoCategory.meeting_context:
        return TodoPriority.medium
    return TodoPriority.low


def recommend_action(category: TodoCategory, repo: str | None, pipeline: str | None) -> str:
    if category == TodoCategory.pipeline_failure:
        parts = ["Open the failed pipeline run"]
        if repo:
            parts.append(f"for repo {repo}")
        if pipeline:
            parts.append(f"and inspect pipeline {pipeline}")
        parts.append(
            "then check the first failing task, recent commits, and environment variables."
        )
        return " ".join(parts)
    if category == TodoCategory.needs_response:
        return "Draft a concise response and confirm any requested dates, owners, or decisions."
    if category == TodoCategory.needs_action:
        return "Review the requested action and decide whether to create follow-up work."
    if category == TodoCategory.meeting_context:
        return "Review before the meeting or attach it to the relevant work item."
    return "Read when time permits; no immediate action detected."


def identify_repo(subject: str, body_preview: str) -> str | None:
    text = f"{subject} {body_preview}"
    patterns = [
        r"repo(?:sitory)?[:\s]+([\w.-]+/[\w.-]+)",
        r"repo(?:sitory)?[:\s]+([\w.-]+)",
        r"([\w.-]+/[\w.-]+)\s+(?:pipeline|build|deployment)",
    ]
    return first_match(patterns, text)


def identify_pipeline(subject: str, body_preview: str) -> str | None:
    text = f"{subject} {body_preview}"
    patterns = [
        r"pipeline[:\s]+([\w .-]+?)(?:\s+#|\s+failed|$)",
        r"build[:\s]+([\w .-]+?)(?:\s+#|\s+failed|$)",
    ]
    return first_match(patterns, text)


def first_match(patterns: list[str], text: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None
