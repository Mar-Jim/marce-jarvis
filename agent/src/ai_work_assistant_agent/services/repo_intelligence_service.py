import subprocess
from pathlib import Path

from ai_work_assistant_agent.domain.repo import (
    GitInfo,
    ProjectType,
    RepoCapability,
    RepoCommand,
    RepoContext,
    RepoFile,
)

IGNORED_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
}


class RepoIntelligenceService:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root.resolve()

    def build_context(self) -> RepoContext:
        files = self._scan_files()
        paths = {file.path for file in files}
        project_types = detect_project_types(paths)
        return RepoContext(
            root=str(self.repo_root),
            git=self._git_info(),
            project_types=project_types,
            files=files,
            important_files=important_files(paths),
            databricks_bundle="databricks.yml" in paths,
            ci_cd=ProjectType.cicd in project_types,
        )

    def explain_architecture(self) -> str:
        context = self.build_context()
        sections = [f"Repository root: {context.root}"]
        sections.append(f"Project types: {', '.join(context.project_types) or 'unknown'}")
        if context.databricks_bundle:
            sections.append(
                "Databricks Asset Bundle detected via databricks.yml. Deployment flow likely "
                "runs through Databricks CLI bundle commands."
            )
        if ProjectType.python in context.project_types:
            sections.append("Python code detected. Use pytest, ruff, and mypy for validation.")
        if ProjectType.sql in context.project_types:
            sections.append("SQL assets detected. Review query dependencies and warehouse targets.")
        if ProjectType.dashboard in context.project_types:
            sections.append("Dashboard-style project detected from dashboard/app artifacts.")
        if context.ci_cd:
            sections.append("CI/CD configuration detected. Review workflow config before releases.")
        sections.append(f"Important files: {', '.join(context.important_files) or 'none'}")
        return "\n".join(sections)

    def explain_deployment_flow(self) -> str:
        context = self.build_context()
        if context.databricks_bundle:
            return (
                "Databricks deployment flow: inspect databricks.yml, select a target, run "
                "`databricks bundle validate`, then deploy/run through approved Databricks CLI "
                "commands. This service only exposes validate as an approved local command."
            )
        if context.ci_cd:
            return (
                "Deployment flow appears CI/CD-driven. Inspect workflow files such as "
                ".github/workflows, azure-pipelines.yml, or .gitlab-ci.yml."
            )
        return "No explicit deployment flow detected from local repository structure."

    def suggest_for_capability(self, capability: RepoCapability) -> list[str]:
        context = self.build_context()
        suggestions = {
            RepoCapability.explain_repo_architecture: [self.explain_architecture()],
            RepoCapability.explain_deployment_flow: [self.explain_deployment_flow()],
            RepoCapability.generate_tests: [
                "Add focused tests near changed Python or TypeScript modules.",
                "Run pytest for backend changes and extension tests for TypeScript client changes.",
            ],
            RepoCapability.find_bugs: [
                "Run ruff, mypy, pytest, and relevant extension tests.",
                "Inspect config files and provider boundaries for unsafe side effects.",
            ],
            RepoCapability.update_configs: [
                "Review databricks.yml, pyproject.toml, package.json, and CI workflow files.",
            ],
            RepoCapability.suggest_edits: [
                "Produce diffs first. Apply file changes only through an approved write call.",
            ],
            RepoCapability.generate_code: [
                "Generate code into a proposed patch. Require approval before writing files.",
            ],
            RepoCapability.refactor_code: [
                "Keep refactors scoped and run tests after approved changes.",
            ],
        }
        base = suggestions[capability]
        if context.databricks_bundle:
            base.append(
                "For DAB changes, validate with `databricks bundle validate` after approval."
            )
        return base

    def run_command(self, command: RepoCommand) -> subprocess.CompletedProcess[str]:
        command_args = {
            RepoCommand.databricks_bundle_validate: ["databricks", "bundle", "validate"],
            RepoCommand.pytest: ["pytest"],
            RepoCommand.ruff: ["ruff", "check", "."],
            RepoCommand.mypy: ["mypy", "."],
        }[command]
        return subprocess.run(
            command_args,
            cwd=self.repo_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )

    def update_file(self, relative_path: str, content: str) -> Path:
        target = self.resolve_relative_path(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def resolve_relative_path(self, relative_path: str) -> Path:
        target = (self.repo_root / relative_path).resolve()
        if target != self.repo_root and self.repo_root not in target.parents:
            raise ValueError("Path escapes repository root")
        return target

    def _scan_files(self) -> list[RepoFile]:
        files: list[RepoFile] = []
        for path in self.repo_root.rglob("*"):
            if not path.is_file() or should_ignore(path, self.repo_root):
                continue
            relative = path.relative_to(self.repo_root).as_posix()
            files.append(
                RepoFile(path=relative, kind=file_kind(path), size_bytes=path.stat().st_size)
            )
        return sorted(files, key=lambda file: file.path)

    def _git_info(self) -> GitInfo:
        return GitInfo(
            is_git_repo=self._git("rev-parse", "--is-inside-work-tree") == "true",
            branch=self._git("branch", "--show-current"),
            commit=self._git("rev-parse", "--short", "HEAD"),
            remote=self._git("remote", "get-url", "origin"),
        )

    def _git(self, *args: str) -> str | None:
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=self.repo_root,
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        output = result.stdout.strip()
        return output or None


def should_ignore(path: Path, repo_root: Path) -> bool:
    relative_parts = path.relative_to(repo_root).parts
    return any(part in IGNORED_DIRS for part in relative_parts)


def file_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".py":
        return "python"
    if suffix == ".sql":
        return "sql"
    if suffix in {".yml", ".yaml"}:
        return "yaml"
    if suffix in {".ts", ".tsx", ".js", ".jsx"}:
        return "typescript"
    if suffix in {".json", ".toml"}:
        return "config"
    return "file"


def detect_project_types(paths: set[str]) -> list[ProjectType]:
    detected: list[ProjectType] = []
    if "databricks.yml" in paths:
        detected.append(ProjectType.databricks_asset_bundle)
    if any(path.endswith(".py") for path in paths) or "pyproject.toml" in paths:
        detected.append(ProjectType.python)
    if any(path.endswith(".sql") for path in paths):
        detected.append(ProjectType.sql)
    if is_dashboard_repo(paths):
        detected.append(ProjectType.dashboard)
    if is_cicd_repo(paths):
        detected.append(ProjectType.cicd)
    if "package.json" in paths or any(path.endswith((".ts", ".tsx")) for path in paths):
        detected.append(ProjectType.typescript)
    return detected or [ProjectType.unknown]


def is_dashboard_repo(paths: set[str]) -> bool:
    dashboard_markers = {
        "app.py",
        "streamlit_app.py",
        "dashboard.py",
        "dash_app.py",
        "powerbi",
        "dashboards",
    }
    return any(path in dashboard_markers or path.startswith("dashboards/") for path in paths)


def is_cicd_repo(paths: set[str]) -> bool:
    return any(
        path.startswith(".github/workflows/")
        or path in {"azure-pipelines.yml", ".gitlab-ci.yml", "Jenkinsfile"}
        for path in paths
    )


def important_files(paths: set[str]) -> list[str]:
    markers = [
        "README.md",
        "databricks.yml",
        "pyproject.toml",
        "package.json",
        "pnpm-workspace.yaml",
        "azure-pipelines.yml",
        ".gitlab-ci.yml",
    ]
    found = [marker for marker in markers if marker in paths]
    found.extend(sorted(path for path in paths if path.startswith(".github/workflows/")))
    return found
