# AI Work Assistant

Enterprise-grade local AI assistant for VS Code, designed for data engineering and data analysis workflows involving Databricks, Python, SQL, Azure DevOps, email, and Databricks Asset Bundles.

This repository is currently in the scaffolding phase. No assistant business logic is implemented yet.

## Goals

- Run locally inside VS Code.
- Use a VS Code extension frontend.
- Use a local Python backend with FastAPI.
- Persist local state in SQLite.
- Support modular, strongly typed tool extensions.
- Require approval before any action that changes files, runs commands, sends messages, or touches external systems.
- Be easy to install, test, version, and evolve.

## Documentation

- [Technical Architecture](./docs/architecture.md)
- [Recommended Repo Structure](./docs/repo-structure.md)
- [Initial Scaffolding](./docs/scaffolding.md)
- [Phased Roadmap](./docs/roadmap.md)
- [Debug, Test, and Deploy Guide](./docs/debug-test-deploy.html)
- [Extension Capabilities Tutorial](./docs/extension-capabilities-tutorial.html)

## Monorepo Layout

```text
ai-work-assistant/
  extension/          VS Code extension frontend
  agent/              Python FastAPI backend
  packages/shared/    Shared TypeScript contracts and utilities
  docs/               Architecture and planning docs
  scripts/            Local development scripts
  tests/              Cross-project tests and fixtures
```

## Local Tooling

- TypeScript workspace: `pnpm`
- Python dependency management: `uv`
- Python linting/formatting: `ruff`
- TypeScript linting/formatting: `eslint` and `prettier`
- Git hooks: `pre-commit`

## Development Commands

```bash
./scripts/bootstrap.sh
./scripts/dev-agent.sh
./scripts/dev-extension.sh
./scripts/lint.sh
./scripts/format.sh
./scripts/test.sh
```

## Current Status

Repository scaffold.

Implementation should start with backend/extension contracts and approval-gated infrastructure before any assistant capabilities are added.
