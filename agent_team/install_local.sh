#!/bin/bash
# 安裝並啟動本機 Agent Team(caffeinate + worker + digest)
set -e
SRC="/Users/delvin/Downloads/Delvin agent/agent_team/launchd"
DST="$HOME/Library/LaunchAgents"
mkdir -p "$DST"
for f in caffeinate worker digest; do
  L="com.marketdaily.agentteam.$f"
  cp "$SRC/$L.plist" "$DST/$L.plist"
  launchctl unload "$DST/$L.plist" 2>/dev/null || true
  launchctl load "$DST/$L.plist"
  echo "✅ 已載入 $L"
done
echo
echo "本機 Agent Team 已啟動:"
echo "  · caffeinate — 充電時不讓 Mac 睡眠"
echo "  · worker     — 每 30 分鐘撿一個任務做"
echo "  · digest     — 每天 07:03 寄晨間匯總"
echo
echo "停用:bash agent_team/uninstall_local.sh"
