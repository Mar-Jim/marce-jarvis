# Recommended Repo Structure

The repository uses a monorepo layout so the VS Code extension, Python agent, shared contracts, documentation, and tests evolve together.

```text
ai-work-assistant/
  README.md
  package.json
  pnpm-workspace.yaml
  tsconfig.base.json
  eslint.config.mjs
  .prettierrc.json
  .pre-commit-config.yaml
  .env.example
  ai-work-assistant.code-workspace

  extension/
    README.md
    package.json
    tsconfig.json
    src/
      extension.ts

  agent/
    README.md
    pyproject.toml
    src/
      ai_work_assistant_agent/
        __init__.py
        main.py
    tests/

  packages/
    shared/
      README.md
      package.json
      tsconfig.json
      src/
        index.ts

  docs/
    README.md
    architecture.md
    repo-structure.md
    scaffolding.md
    roadmap.md

  scripts/
    bootstrap.sh
    dev-agent.sh
    dev-extension.sh
    package-extension.sh

  .vscode/
    launch.json
    tasks.json

  tests/
    README.md
```

## Directory Responsibilities

`extension`

The VS Code extension frontend. It owns the activity bar view, webview UI, command palette entries, backend lifecycle, and calls into the local backend API.

`agent`

The FastAPI backend. It owns assistant orchestration, tool execution, approval policy, SQLite persistence, and integration adapters.

`packages/shared`

Shared TypeScript contracts. This can hold generated API clients, shared TypeScript types, and compatibility tests.

`docs`

Architecture, design decisions, roadmap, runbooks, and future feature specifications.

`scripts`

Small local developer scripts. These should be thin wrappers around standard tools and should not hide complex behavior.

`.github/workflows`

CI definitions for linting, type checks, tests, and packaging validation.

`.vscode`

Checked-in VS Code launch and task configuration for local development.

`tests`

Cross-project tests, fixtures, and future end-to-end smoke tests.

## Naming Conventions

- Python package: `ai_work_assistant_agent`
- Extension package: `@ai-work-assistant/extension`
- Workspace package: `ai-work-assistant`
- Public API path prefix: `/api/v1`
- Tool names: lowercase dotted names such as `filesystem.search`, `databricks.bundle.validate`
- Database migrations: timestamped and descriptive

## Design Constraints For The Structure

- Keep extension and backend deployable independently during development.
- Keep generated shared files under `packages/shared/generated` once contract generation exists.
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
