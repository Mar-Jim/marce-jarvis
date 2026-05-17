#!/usr/bin/env bash
set -euo pipefail

corepack pnpm test
uv run --project agent pytest
