#!/usr/bin/env bash
set -euo pipefail

corepack pnpm lint
uv run --project agent ruff check agent
uv run --project agent mypy agent/src
