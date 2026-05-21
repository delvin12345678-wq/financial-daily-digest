#!/bin/bash
# 晨間匯總 — 每天早上由 launchd 觸發
REPO="/Users/delvin/Downloads/Delvin agent"
cd "$REPO" || exit 1
mkdir -p agent_team/logs
LOG="agent_team/logs/digest-$(date +%Y%m%d).log"
{
  echo "=== $(date '+%F %T') digest start ==="
  /usr/bin/git pull --rebase --autostash || true
  /usr/bin/python3 agent_team/notify.py digest
  /usr/bin/git add -A agent_team/
  /usr/bin/git commit -m "🤖 [agent-team] 晨間匯總" || true
  /usr/bin/git push || true
  echo "=== $(date '+%F %T') digest end ==="
} >> "$LOG" 2>&1
