#!/usr/bin/env bash
set -euo pipefail

pnpm install
uv sync --project agent --extra dev
uv run --project agent pre-commit install
