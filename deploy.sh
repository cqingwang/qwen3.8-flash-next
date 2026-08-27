#!/usr/bin/env bash
# Qwen3.8-Flash-Next 双机部署入口：仅命令解析，具体实现见 program.py。
# 用法与 ../deepseek-flash/deploy.sh 对齐；在任意能 SSH 到 spark-a 的机器执行。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROGRAM="$SCRIPT_DIR/program.py"
CONFIG="${CONFIG:-$SCRIPT_DIR/config.yaml}"

[ -f "$PROGRAM" ] || { echo "[FAIL] missing $PROGRAM" >&2; exit 1; }
[ -f "$CONFIG" ] || { echo "[FAIL] missing $CONFIG" >&2; exit 1; }

CMD="${1#--}"
shift || true
case "$CMD" in
  ""|help|-h) exec python3 "$PROGRAM" --config "$CONFIG" help "$@" ;;
  *)           exec python3 "$PROGRAM" --config "$CONFIG" "$CMD" "$@" ;;
esac
