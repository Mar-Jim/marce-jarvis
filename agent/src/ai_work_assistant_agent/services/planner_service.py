from datetime import UTC, datetime

from ai_work_assistant_agent.api.schemas.todos import TodoCategory, TodoPriority, TodoStatus
from ai_work_assistant_agent.domain.planner import PlannedWorkItem, WorkPlan
from ai_work_assistant_agent.domain.todos import Todo
from ai_work_assistant_agent.services.repo_intelligence_service import RepoIntelligenceService


class PlannerService:
    def __init__(self, repo_service: RepoIntelligenceService) -> None:
        self.repo_service = repo_service

    def build_plan(self, todos: list[Todo]) -> WorkPlan:
        repo_context = self.repo_service.build_context()
        active_todos = [todo for todo in todos if todo.status not in done_statuses()]
        planned = [score_todo(todo, datetime.now(UTC)) for todo in active_todos]
        planned.sort(key=lambda item: (-item.score, effort_sort(item.estimated_effort), item.title))
        ranked = [
            PlannedWorkItem(
                todo_id=item.todo_id,
                title=item.title,
                score=item.score,
                rank=index + 1,
                estimated_effort=item.estimated_effort,
                category=item.category,
                source=item.source,
                external_id=item.external_id,
                reasons=item.reasons,
                suggested_ticket_update=item.suggested_ticket_update,
            )
            for index, item in enumerate(planned)
        ]
        return WorkPlan(
            prioritized_work=ranked,
            recommended_next_task=ranked[0] if ranked else None,
            optimization_summary=optimization_summary(ranked, repo_context.project_types),
        )


def score_todo(todo: Todo, now: datetime) -> PlannedWorkItem:
    score = 0
    reasons: list[str] = []

    priority_score = {
        TodoPriority.urgent: 50,
        TodoPriority.high: 35,
        TodoPriority.medium: 20,
        TodoPriority.low: 5,
    }[todo.priority]
    score += priority_score
    reasons.append(f"{todo.priority.value} priority (+{priority_score})")

    category_score = {
        TodoCategory.pipeline_failure: 70,
        TodoCategory.blocked: 60,
        TodoCategory.urgent: 55,
        TodoCategory.due_soon: 40,
        TodoCategory.needs_action: 35,
        TodoCategory.needs_response: 30,
        TodoCategory.in_progress: 25,
        TodoCategory.meeting_context: 10,
        TodoCategory.informational: 0,
        TodoCategory.normal: 0,
    }[todo.category]
    if category_score:
        score += category_score
        reasons.append(f"{todo.category.value} category (+{category_score})")

    if todo.due_at is not None:
        due_at = normalize_datetime(todo.due_at)
        if due_at < now:
            score += 45
            reasons.append("overdue (+45)")
        elif (due_at - now).days <= 2:
            score += 25
            reasons.append("due soon (+25)")

    if todo.status == TodoStatus.in_progress:
        score += 15
        reasons.append("already in progress, reduces context switching (+15)")

    if todo.external_provider == "azure_devops":
        score += 10
        reasons.append("linked Azure DevOps ticket (+10)")
    if todo.external_provider == "outlook":
        score += 5
        reasons.append("derived from unread email (+5)")

    return PlannedWorkItem(
        todo_id=todo.id,
        title=todo.title,
        score=score,
        rank=0,
        estimated_effort=estimate_effort(todo),
        category=todo.category.value,
        source=todo.source,
        external_id=todo.external_id,
        reasons=reasons,
        suggested_ticket_update=suggest_ticket_update(todo),
    )


def estimate_effort(todo: Todo) -> str:
    text = f"{todo.title} {todo.description}".lower()
    if todo.category == TodoCategory.pipeline_failure:
        return "30-60 min"
    if any(term in text for term in ["refactor", "migration", "architecture"]):
        return "2-4 hours"
    if any(term in text for term in ["fix", "bug", "test", "config"]):
        return "30-90 min"
    if todo.category in {TodoCategory.needs_response, TodoCategory.meeting_context}:
        return "10-20 min"
    return "30-60 min"


def effort_sort(estimated_effort: str) -> int:
    order = {
        "10-20 min": 1,
        "30-60 min": 2,
        "30-90 min": 3,
        "2-4 hours": 4,
    }
    return order.get(estimated_effort, 99)


def suggest_ticket_update(todo: Todo) -> str | None:
    if todo.external_provider != "azure_devops":
        return None
    if todo.category == TodoCategory.blocked:
        return "Update ticket state/comment with blocker, owner needed, and next dependency."
    if todo.category == TodoCategory.pipeline_failure:
        return (
            "Update ticket with failed pipeline, suspected failing step, "
            "and investigation owner."
        )
    if todo.status == TodoStatus.in_progress:
        return "Update ticket with current progress and next validation step."
    return "Add a short status comment after the next work session."


def optimization_summary(items: list[PlannedWorkItem], project_types: object) -> str:
    if not items:
        return "No active work found. Sync tickets, unread emails, or add todos."
    top = items[0]
    return (
        "Plan is sorted by blocker and production urgency first, then due dates, current "
        f"in-progress work, and linked external context. Recommended next task: {top.title}."
    )


def done_statuses() -> set[TodoStatus]:
    return {TodoStatus.done, TodoStatus.canceled}


def normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
