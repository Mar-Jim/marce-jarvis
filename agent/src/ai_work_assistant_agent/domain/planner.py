from dataclasses import dataclass


@dataclass(frozen=True)
class PlannedWorkItem:
    todo_id: str
    title: str
    score: int
    rank: int
    estimated_effort: str
    category: str
    source: str
    external_id: str | None
    reasons: list[str]
    suggested_ticket_update: str | None


@dataclass(frozen=True)
class WorkPlan:
    prioritized_work: list[PlannedWorkItem]
    recommended_next_task: PlannedWorkItem | None
    optimization_summary: str
