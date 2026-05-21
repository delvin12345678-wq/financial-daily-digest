#!/bin/bash
# 本機夜間 Worker — 每 30 分鐘由 launchd 觸發
REPO="/Users/delvin/Downloads/Delvin agent"
CLAUDE="/Applications/cmux.app/Contents/Resources/bin/claude"
cd "$REPO" || exit 1
mkdir -p agent_team/logs
LOG="agent_team/logs/worker-$(date +%Y%m%d).log"
LOCK="agent_team/.worker.lock"

if ! mkdir "$LOCK" 2>/dev/null; then
  echo "$(date '+%F %T') 已有 worker 執行中,跳過" >> "$LOG"
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

{
  echo "=== $(date '+%F %T') worker start ==="
  /usr/bin/caffeinate -i "$CLAUDE" -p "你是 MarketDaily Agent Team 的夜間 Worker。請讀取並嚴格依照 agent_team/worker.md 的指令,執行一次值班。" --dangerously-skip-permissions
  echo "=== $(date '+%F %T') worker end ==="
} >> "$LOG" 2>&1
