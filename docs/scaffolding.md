# Initial Scaffolding

This document defines the initial scaffold to create before feature implementation. It is intentionally documentation-only for now.

## Scaffold Phase Objectives

The first implementation phase should create a working local development shell without building assistant features.

The scaffold should prove:

- VS Code extension can start.
- Python backend can start locally.
- Extension can call backend health endpoint.
- SQLite database can be initialized.
- Tests, linting, typing, and CI can run.
- API contracts can be versioned.
- Feature code has clear places to live later.

## Backend Scaffold

Create `agent` with:

- `pyproject.toml`
- `src/ai_work_assistant_agent/main.py`
- `tests/README.md`

Initial backend behavior:

- Start FastAPI locally.
- Keep route, persistence, assistant, model, and tool behavior out until implementation begins.
- Avoid assistant, model, and tool features.

Recommended backend dependencies:

- `fastapi`
- `uvicorn`
- `pydantic`
- `pydantic-settings`
- `sqlalchemy` or `sqlmodel`
- `alembic`
- `pytest`
- `httpx`
- `ruff`
- `mypy` or `pyright`

## VS Code Extension Scaffold

Create `extension` with:

- `package.json`
- `tsconfig.json`
- `src/extension.ts`
- `test`

Initial extension behavior:

- Compile as a VS Code extension.
- Keep commands, webviews, backend lifecycle, and chat UI out until implementation begins.
- Avoid assistant chat and tool execution features.

Recommended extension dependencies:

- TypeScript
- VS Code extension test tooling
- A webview UI framework only if needed
- ESLint or Biome
- Vitest or equivalent unit test runner

## Contracts Scaffold

Create `packages/shared` with:

- TypeScript package metadata.
- Strict TypeScript config.
- Empty public export.

Initial contract rules:

- Backend API is the source of truth.
- Extension consumes generated or checked TypeScript types.
- API changes must update contract artifacts.

## Development Commands

The repo should eventually support:

```text
make setup
make backend-dev
make extension-dev
make test
make lint
make typecheck
make package
```

Each command should call simple underlying tools so failures are easy to debug.

## GitHub And CI Scaffold

Add CI after the first backend and extension skeletons exist.

Initial CI checks:

- Backend lint.
- Backend type check.
- Backend tests.
- Extension lint.
- Extension type check.
- Extension tests.
- Contract drift check.

## Local Configuration Scaffold

Add:

- `.env.example`
- `.gitignore`
- VS Code launch config.
- VS Code tasks config.

Do not commit:

- `.env`
- SQLite databases.
- generated logs.
- local model files.
- credentials.
- Databricks profiles.
- Azure DevOps tokens.

## Definition Of Done For Scaffold

The scaffold is complete when:

- A developer can clone the repo and run setup.
- Backend health endpoint responds locally.
- VS Code extension can open an assistant panel.
- Extension can display backend health.
- SQLite can be created in a local ignored path.
- CI validates linting, typing, and tests.
- No feature-specific assistant behavior exists yet.
