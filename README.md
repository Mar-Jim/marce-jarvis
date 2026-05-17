# Marce Jarvis

Local-first AI assistant for VS Code, designed for data engineering and data analysis workflows involving Databricks, Python, SQL, Azure DevOps, email, and Databricks Asset Bundles.

This repository is currently in the planning and scaffolding phase. No product features are implemented yet.

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

## Current Status

Documentation-only scaffold.

Implementation should start with the repository skeleton, local development workflow, and backend/extension contracts before any assistant capabilities are added.
