# Recommended Repo Structure

The repository should use a monorepo layout so the VS Code extension, Python backend, shared contracts, documentation, and tests evolve together.

```text
marce-jarvis/
  README.md
  docs/
    architecture.md
    repo-structure.md
    scaffolding.md
    roadmap.md

  apps/
    vscode-extension/
      package.json
      tsconfig.json
      src/
        extension.ts
        backend/
          client.ts
          lifecycle.ts
        webview/
          main.tsx
          components/
        commands/
        types/
      test/

    backend/
      pyproject.toml
      src/
        marce_jarvis/
          __init__.py
          main.py
          api/
            app.py
            routers/
          core/
            config.py
            logging.py
            security.py
          domain/
            approvals.py
            conversations.py
            tools.py
          services/
            assistant_service.py
            approval_service.py
            tool_service.py
          persistence/
            database.py
            migrations/
            repositories/
          tools/
            registry.py
            base.py
            filesystem/
            databricks/
            azure_devops/
            email/
            python/
            sql/
          providers/
            base.py
            local_model.py
      tests/

  packages/
    contracts/
      openapi/
      schemas/
      generated/

  scripts/
    bootstrap.sh
    dev-backend.sh
    dev-extension.sh
    package-extension.sh

  .github/
    workflows/
      ci.yml

  .vscode/
    launch.json
    tasks.json

  .gitignore
  Makefile
```

## Directory Responsibilities

`apps/vscode-extension`

The VS Code extension frontend. It owns the activity bar view, webview UI, command palette entries, backend lifecycle, and calls into the local backend API.

`apps/backend`

The FastAPI backend. It owns assistant orchestration, tool execution, approval policy, SQLite persistence, and integration adapters.

`packages/contracts`

Shared API contracts. This can hold OpenAPI exports, generated TypeScript clients, generated Python schemas if needed, and compatibility tests.

`docs`

Architecture, design decisions, roadmap, runbooks, and future feature specifications.

`scripts`

Small local developer scripts. These should be thin wrappers around standard tools and should not hide complex behavior.

`.github/workflows`

CI definitions for linting, type checks, tests, and packaging validation.

`.vscode`

Checked-in VS Code launch and task configuration for local development.

## Naming Conventions

- Python package: `marce_jarvis`
- Extension package: `marce-jarvis`
- Public API path prefix: `/api/v1`
- Tool names: lowercase dotted names such as `filesystem.search`, `databricks.bundle.validate`
- Database migrations: timestamped and descriptive

## Design Constraints For The Structure

- Keep extension and backend deployable independently during development.
- Keep generated files under `packages/contracts/generated`.
- Keep tests next to the app they validate.
- Keep tool implementations isolated by domain.
- Keep docs separate from implementation until feature work starts.

## Future Expansion Points

Potential future directories:

```text
  examples/
    sample-dab-project/
    sample-sql-project/

  evals/
    assistant-turns/
    tool-safety/

  packaging/
    vsix/
    backend-wheel/
```

These should be added only when the implementation needs them.
