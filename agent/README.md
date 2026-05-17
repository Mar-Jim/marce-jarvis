# Python Agent

Local FastAPI backend for AI Work Assistant.

This package currently contains scaffolding only. It should own:

- Local API surface.
- Assistant orchestration.
- Approval policy.
- Tool registry.
- SQLite persistence.
- Integration adapters.

No AI behavior is implemented yet.

## Endpoints

- `GET /health`
- `GET /todos`
- `POST /todos`
- `PATCH /todos/{id}`
- `POST /integrations/azure-devops/sync`
- `POST /integrations/azure-devops/update-progress`
- `POST /api/v1/chat/turn` placeholder used by the VS Code extension shell

## Local Startup

From the repository root:

```bash
uv sync --project agent --extra dev
uv run --project agent uvicorn ai_work_assistant_agent.main:app --host 127.0.0.1 --port 8765 --reload
```

If `uv` is installed as a Python module rather than a shell command, use:

```bash
python3 -m uv sync --project agent --extra dev
python3 -m uv run --project agent uvicorn ai_work_assistant_agent.main:app --host 127.0.0.1 --port 8765 --reload
```

Or use the repo script:

```bash
./scripts/dev-agent.sh
```

The default SQLite database path is `.local/ai-work-assistant.sqlite3`. Override it with:

```bash
AI_WORK_ASSISTANT_SQLITE_PATH=/path/to/local.sqlite3
```

## Azure DevOps

Azure DevOps integration uses a provider abstraction under `integrations/`. The current provider supports Personal Access Token authentication. PATs must be supplied per request in the `X-Azure-DevOps-PAT` header and are not persisted by the backend.

The integration does not hardcode organization or project names. The caller must provide both values.

## Tests

```bash
uv run --project agent pytest
```
