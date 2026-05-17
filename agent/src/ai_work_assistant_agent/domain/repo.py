from dataclasses import dataclass
from enum import StrEnum


class ProjectType(StrEnum):
    databricks_asset_bundle = "databricks_asset_bundle"
    python = "python"
    sql = "sql"
    dashboard = "dashboard"
    cicd = "cicd"
    typescript = "typescript"
    unknown = "unknown"


class RepoCommand(StrEnum):
    databricks_bundle_validate = "databricks_bundle_validate"
    pytest = "pytest"
    ruff = "ruff"
    mypy = "mypy"


class RepoCapability(StrEnum):
    explain_repo_architecture = "explain_repo_architecture"
    suggest_edits = "suggest_edits"
    generate_code = "generate_code"
    refactor_code = "refactor_code"
    update_configs = "update_configs"
    generate_tests = "generate_tests"
    explain_deployment_flow = "explain_deployment_flow"
    find_bugs = "find_bugs"


@dataclass(frozen=True)
class RepoFile:
    path: str
    kind: str
    size_bytes: int


@dataclass(frozen=True)
class GitInfo:
    is_git_repo: bool
    branch: str | None
    commit: str | None
    remote: str | None


@dataclass(frozen=True)
class RepoContext:
    root: str
    git: GitInfo
    project_types: list[ProjectType]
    files: list[RepoFile]
    important_files: list[str]
    databricks_bundle: bool
    ci_cd: bool
