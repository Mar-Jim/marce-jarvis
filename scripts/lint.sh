#!/usr/bin/env bash
set -euo pipefail

pnpm lint
uv run --project agent ruff check agent
uv run --project agent mypy agent/src
