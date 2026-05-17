from fastapi import APIRouter, Request
from pydantic import BaseModel

from ai_work_assistant_agent.core.config import Settings
from ai_work_assistant_agent.persistence.todo_repository import TodoRepository
from ai_work_assistant_agent.services.planner_service import PlannerService
from ai_work_assistant_agent.services.repo_intelligence_service import RepoIntelligenceService

router = APIRouter(prefix="/planner", tags=["planner"])


class PlannedWorkItemResponse(BaseModel):
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


class WorkPlanResponse(BaseModel):
    prioritized_work: list[PlannedWorkItemResponse]
    recommended_next_task: PlannedWorkItemResponse | None
    optimization_summary: str


@router.get("/plan", response_model=WorkPlanResponse)
def build_plan(request: Request) -> WorkPlanResponse:
    settings: Settings = request.app.state.settings
    repository = TodoRepository(request.app.state.database)
    service = PlannerService(RepoIntelligenceService(settings.repo_root))
    plan = service.build_plan(repository.list())
    items = [
        PlannedWorkItemResponse(
            todo_id=item.todo_id,
            title=item.title,
            score=item.score,
            rank=item.rank,
            estimated_effort=item.estimated_effort,
            category=item.category,
            source=item.source,
            external_id=item.external_id,
            reasons=item.reasons,
            suggested_ticket_update=item.suggested_ticket_update,
        )
        for item in plan.prioritized_work
    ]
    return WorkPlanResponse(
        prioritized_work=items,
        recommended_next_task=items[0] if items else None,
        optimization_summary=plan.optimization_summary,
    )
