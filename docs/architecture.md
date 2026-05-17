# Technical Architecture

## Product Shape

Marce Jarvis is a local AI assistant that runs inside VS Code and supports a data engineer/data analyst workflow. The assistant is built as a VS Code extension backed by a local Python service. It is local-first, requires no hosted backend, and persists user data in SQLite.

The system should optimize for:

- Fast access from VS Code.
- Safe interaction with local files, terminals, Databricks projects, SQL, and Azure DevOps workflows.
- Explicit approval before side effects.
- Extensible tools with typed contracts.
- Testable boundaries between UI, backend orchestration, persistence, and integrations.

## High-Level Components

```text
VS Code Extension
  - Webview UI
  - Command palette commands
  - Workspace context provider
  - Approval prompts
  - Local backend lifecycle manager

Local Python Backend
  - FastAPI HTTP API
  - Assistant orchestration
  - Tool registry
  - Approval policy engine
  - SQLite persistence
  - Local model/provider adapter layer

SQLite Database
  - Conversations
  - Tool calls
  - Approval decisions
  - Workspace indexes
  - User preferences

Local Tools
  - Filesystem read/search
  - Python and SQL analysis helpers
  - Databricks Asset Bundle helpers
  - Databricks CLI wrappers
  - Azure DevOps CLI/API wrappers
  - Email draft helpers
```

## Runtime Architecture

The VS Code extension owns the user experience and starts the Python backend as a local child process. The backend listens on localhost only and exposes a versioned FastAPI API.

Recommended local flow:

1. User opens the assistant panel or runs a VS Code command.
2. Extension starts the backend if it is not already running.
3. Extension sends workspace context and user request to the backend.
4. Backend builds an assistant turn using configured model/provider adapters and registered tools.
5. Any proposed side effect is returned as an approval request.
6. Extension presents the approval request in VS Code.
7. Backend executes approved actions and stores an auditable record in SQLite.

## Local Backend Boundary

The backend should expose stable HTTP endpoints rather than coupling the extension directly to Python internals.

Initial API surface:

- `GET /health`
- `GET /version`
- `POST /api/v1/chat/turn`
- `GET /api/v1/conversations`
- `GET /api/v1/conversations/{conversation_id}`
- `POST /api/v1/tools/preview`
- `POST /api/v1/tools/execute`
- `POST /api/v1/approvals/{approval_id}/decision`

All request and response bodies should be defined with Pydantic models. The VS Code extension should mirror these contracts with generated or manually maintained TypeScript types.

## VS Code Extension Frontend

The extension should provide:

- Activity bar view for the assistant.
- Webview-based chat and tool approval UI.
- Command palette entries for common workflows.
- Workspace-aware context collection.
- Status bar indicator for backend availability.
- Local backend process management.

The extension should not contain business logic for assistant orchestration. It should own UI state, VS Code integration, local process lifecycle, and approval interactions.

## Python Backend

The backend should be organized around explicit service boundaries:

- API routers: FastAPI endpoint definitions.
- Application services: assistant turns, approvals, tool execution.
- Domain models: strongly typed internal objects.
- Persistence repositories: SQLite access.
- Tool plugins: isolated capabilities with schemas and safety metadata.
- Provider adapters: local model or enterprise-approved model access.

Recommended baseline stack:

- FastAPI for API service.
- Pydantic for typed contracts.
- SQLAlchemy or SQLModel for SQLite persistence.
- Alembic for migrations.
- pytest for backend tests.
- ruff for linting and formatting.
- mypy or pyright for static typing.

## Persistence Model

SQLite should be the default local database. It should live under the extension global storage path or a user-configurable local path.

Core tables:

- `conversations`: conversation metadata.
- `messages`: user, assistant, system, and tool messages.
- `tool_calls`: requested and completed tool calls.
- `approvals`: approval requests and decisions.
- `workspace_snapshots`: workspace metadata captured at a point in time.
- `settings`: local user preferences and feature flags.

Sensitive data should be minimized. Store references and summaries where possible instead of full file contents, emails, or secrets.

## Tool Architecture

Tools should be registered through a typed interface.

Each tool should define:

- Name and description.
- Input schema.
- Output schema.
- Required permissions.
- Side-effect classification.
- Preview capability when possible.
- Execution function.
- Audit metadata.

Side-effect classes:

- `read_only`: reads local or external data.
- `local_write`: edits files or local SQLite state.
- `command`: runs a local command.
- `external_write`: mutates external systems such as Azure DevOps, Databricks, or email.
- `secret_access`: accesses credentials or tokens.

Approval should be required for every class except low-risk `read_only` actions. Some read-only actions may still require approval when they access sensitive locations or external systems.

## Safety Model

The assistant should be safe by default.

Required controls:

- Approval gates before file edits, shell commands, Databricks mutations, Azure DevOps updates, and email sends.
- Dry-run or preview for tools that can provide it.
- Audit log for tool requests, approvals, denials, and execution results.
- Workspace-root restriction for file writes unless explicitly approved.
- Command allowlist and denylist.
- Secret redaction in logs and UI.
- Clear distinction between draft generation and action execution.

Approval prompts should include:

- Tool name.
- Exact proposed action.
- Files, commands, or external resources affected.
- Risk level.
- Preview or diff when available.
- Allow once, deny, and optionally remember decision for scoped cases.

## Databricks And DAB Support

Databricks support should start as local project intelligence before external mutations.

Initial capabilities to design for:

- Detect `databricks.yml` and bundle structure.
- Explain bundle targets, resources, variables, and jobs.
- Validate local bundle configuration using the Databricks CLI with approval.
- Generate draft bundle changes without applying them automatically.
- Summarize deployment plans.

Mutation capabilities such as deploy, run, or destroy should require explicit approval every time.

## SQL And Python Workflow Support

The assistant should support:

- SQL explanation and refactoring.
- Query linting and performance review.
- Python notebook/script review.
- Test generation suggestions.
- Local project search.
- Dependency and environment explanation.

Execution should remain gated. Running Python scripts, notebooks, SQL queries, or shell commands should require approval.

## Azure DevOps Support

Azure DevOps integration should be tool-based and approval-gated.

Candidate tools:

- Read work items.
- Draft work item updates.
- Summarize PRs.
- Draft PR descriptions.
- Create branches or commits locally.
- Push or update PRs only after approval.

The first implementation should prefer CLI wrappers or enterprise-approved authentication paths instead of introducing a custom cloud service.

## Email Support

Email support should begin with drafting only.

Initial safe capabilities:

- Draft status updates.
- Summarize copied email text.
- Produce meeting follow-up drafts.

Sending email, modifying calendar entries, or reading mailboxes should be separate tool classes and require explicit approval plus connector-specific configuration.

## Configuration

Configuration should be layered:

1. Default settings committed to the repo.
2. User settings in VS Code.
3. Local config file ignored by Git.
4. Environment variables for secrets and enterprise-specific paths.

No secrets should be committed. The assistant should detect missing credentials and surface setup instructions without printing secret values.

## Testing Strategy

Testing should cover each boundary:

- Backend unit tests for services, policies, and tools.
- Backend integration tests for FastAPI routes and SQLite repositories.
- Contract tests for API request/response schemas.
- Extension unit tests for client behavior and state handling.
- Extension integration tests for backend lifecycle and webview messaging.
- End-to-end smoke tests for startup, chat turn, approval request, approval decision, and audit persistence.

## Packaging And Local Installation

The project should support:

- `make setup` or equivalent local bootstrap.
- Python virtual environment creation.
- Node dependency installation for the extension.
- VS Code extension launch/debug profile.
- Local backend launch/debug profile.
- Optional extension packaging into `.vsix`.

Implementation should prioritize a boring, repeatable developer workflow over clever automation.
