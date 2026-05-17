#!/usr/bin/env bash
set -euo pipefail

uv run --project agent uvicorn ai_work_assistant_agent.main:app --host 127.0.0.1 --port 8765 --reload
