#!/usr/bin/env bash
set -euo pipefail

if command -v uv >/dev/null 2>&1; then
  UV=(uv)
else
  UV=(python3 -m uv)
fi

"${UV[@]}" run --project agent uvicorn ai_work_assistant_agent.main:app --host 127.0.0.1 --port 8765 --reload
