from typing import Annotated, Literal

from fastapi import APIRouter, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from ai_work_assistant_agent.core.config import Settings
from ai_work_assistant_agent.domain.repo import RepoCapability, RepoCommand
from ai_work_assistant_agent.services.repo_intelligence_service import RepoIntelligenceService

router = APIRouter(prefix="/repo", tags=["repo"])

ApprovalHeader = Annotated[str | None, Header(alias="X-Approval-Decision")]


class GitInfoResponse(BaseModel):
    is_git_repo: bool
    branch: str | None
    commit: str | None
    remote: str | None


class RepoFileResponse(BaseModel):
    path: str
    kind: str
    size_bytes: int


class RepoContextResponse(BaseModel):
    root: str
    git: GitInfoResponse
    project_types: list[str]
    files: list[RepoFileResponse]
    important_files: list[str]
    databricks_bundle: bool
    ci_cd: bool


class RepoExplanationResponse(BaseModel):
    summary: str


class RepoCapabilityRequest(BaseModel):
    capability: RepoCapability


class RepoCapabilityResponse(BaseModel):
    suggestions: list[str]


class RepoCommandRequest(BaseModel):
    command: RepoCommand


class RepoCommandResponse(BaseModel):
    command: RepoCommand
    approved: bool
    exit_code: int | None
    stdout: str
    stderr: str


class FileUpdateRequest(BaseModel):
    relative_path: str = Field(min_length=1, max_length=1000)
    content: str


class FileUpdateResponse(BaseModel):
    approved: bool
    path: str | None
    message: str


class ApprovalRequiredResponse(BaseModel):
    approval_required: Literal[True]
    action: str
    risk: str


@router.get("/context", response_model=RepoContextResponse)
def get_repo_context(request: Request) -> RepoContextResponse:
    context = get_service(request).build_context()
    return RepoContextResponse(
        root=context.root,
        git=GitInfoResponse(
            is_git_repo=context.git.is_git_repo,
            branch=context.git.branch,
            commit=context.git.commit,
            remote=context.git.remote,
        ),
        project_types=[project_type.value for project_type in context.project_types],
        files=[
            RepoFileResponse(path=file.path, kind=file.kind, size_bytes=file.size_bytes)
            for file in context.files
        ],
        important_files=context.important_files,
        databricks_bundle=context.databricks_bundle,
        ci_cd=context.ci_cd,
    )


@router.get("/architecture", response_model=RepoExplanationResponse)
def explain_repo_architecture(request: Request) -> RepoExplanationResponse:
    return RepoExplanationResponse(summary=get_service(request).explain_architecture())


@router.get("/deployment-flow", response_model=RepoExplanationResponse)
def explain_deployment_flow(request: Request) -> RepoExplanationResponse:
    return RepoExplanationResponse(summary=get_service(request).explain_deployment_flow())


@router.post("/capabilities", response_model=RepoCapabilityResponse)
def repo_capability(
    payload: RepoCapabilityRequest,
    request: Request,
) -> RepoCapabilityResponse:
    return RepoCapabilityResponse(
        suggestions=get_service(request).suggest_for_capability(payload.capability)
    )


@router.post(
    "/commands/run",
    response_model=RepoCommandResponse | ApprovalRequiredResponse,
)
def run_repo_command(
    payload: RepoCommandRequest,
    request: Request,
    approval_decision: ApprovalHeader = None,
) -> RepoCommandResponse | ApprovalRequiredResponse:
    if approval_decision != "approved":
        return ApprovalRequiredResponse(
            approval_required=True,
            action=f"run_repo_command:{payload.command.value}",
            risk="Runs a local command in the configured repository root.",
        )

    result = get_service(request).run_command(payload.command)
    return RepoCommandResponse(
        command=payload.command,
        approved=True,
        exit_code=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )


@router.post(
    "/files/update",
    response_model=FileUpdateResponse | ApprovalRequiredResponse,
)
def update_repo_file(
    payload: FileUpdateRequest,
    request: Request,
    approval_decision: ApprovalHeader = None,
) -> FileUpdateResponse | ApprovalRequiredResponse:
    if approval_decision != "approved":
        return ApprovalRequiredResponse(
            approval_required=True,
            action=f"update_file:{payload.relative_path}",
            risk="Modifies a file under the configured repository root.",
        )

    try:
        path = get_service(request).update_file(payload.relative_path, payload.content)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return FileUpdateResponse(
        approved=True,
        path=str(path),
        message="File updated",
    )


def get_service(request: Request) -> RepoIntelligenceService:
    settings: Settings = request.app.state.settings
    return RepoIntelligenceService(settings.repo_root)
