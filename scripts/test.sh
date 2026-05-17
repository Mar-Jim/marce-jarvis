#!/usr/bin/env bash
set -euo pipefail

pnpm test
uv run --project agent pytest
