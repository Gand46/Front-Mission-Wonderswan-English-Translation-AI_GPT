#!/usr/bin/env bash
export PYTHONDONTWRITEBYTECODE=1
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"; exec "$ROOT/bin/ws-patch-tools" "$@"
