#!/usr/bin/env bash
set -euo pipefail

corepack pnpm format
uv run --project agent ruff format agent
uv run --project agent ruff check --fix agent
