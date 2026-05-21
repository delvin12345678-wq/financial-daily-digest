#!/bin/bash
# 停用並移除本機 Agent Team
DST="$HOME/Library/LaunchAgents"
for f in caffeinate worker digest; do
  L="com.marketdaily.agentteam.$f"
  launchctl unload "$DST/$L.plist" 2>/dev/null || true
  rm -f "$DST/$L.plist"
  echo "🛑 已停用 $L"
done
echo "本機 Agent Team 已關閉。"
