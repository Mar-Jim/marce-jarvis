#!/usr/bin/env bash
set -euo pipefail

if command -v uv >/dev/null 2>&1; then
  UV=(uv)
else
  UV=(python3 -m uv)
fi

corepack pnpm install
"${UV[@]}" sync --project agent --extra dev
"${UV[@]}" run --project agent pre-commit install
