#!/usr/bin/env bash
set -euo pipefail

if command -v uv >/dev/null 2>&1; then
  UV=(uv)
else
  UV=(python3 -m uv)
fi

corepack pnpm lint
"${UV[@]}" run --project agent ruff check agent
"${UV[@]}" run --project agent mypy agent/src
