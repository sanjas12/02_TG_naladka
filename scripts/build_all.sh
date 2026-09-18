#!/usr/bin/env bash
set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Шаг 1: зависимости ==="
bash "$SCRIPTS_DIR/recreate_env.sh"

echo "=== Шаг 2: сборка ==="
bash "$SCRIPTS_DIR/build.sh"
