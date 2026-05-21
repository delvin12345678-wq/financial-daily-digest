#!/bin/bash
# 安裝並啟動本機 Agent Team(caffeinate + worker + digest)
# 從哪一份 repo clone 執行,就裝成指向那份 clone —— 路徑自動偵測,不寫死
set -e
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DST="$HOME/Library/LaunchAgents"
LOGS="$REPO/agent_team/logs"
mkdir -p "$DST" "$LOGS"

cat > "$DST/com.marketdaily.agentteam.caffeinate.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.marketdaily.agentteam.caffeinate</string>
  <key>ProgramArguments</key><array><string>/usr/bin/caffeinate</string><string>-s</string></array>
  <key>KeepAlive</key><true/>
  <key>RunAtLoad</key><true/>
</dict>
</plist>
EOF

cat > "$DST/com.marketdaily.agentteam.worker.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.marketdaily.agentteam.worker</string>
  <key>ProgramArguments</key><array><string>/bin/bash</string><string>$REPO/agent_team/run_worker.sh</string></array>
  <key>StartInterval</key><integer>1800</integer>
  <key>RunAtLoad</key><false/>
  <key>StandardOutPath</key><string>$LOGS/launchd-worker.log</string>
  <key>StandardErrorPath</key><string>$LOGS/launchd-worker.err</string>
</dict>
</plist>
EOF

cat > "$DST/com.marketdaily.agentteam.digest.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.marketdaily.agentteam.digest</string>
  <key>ProgramArguments</key><array><string>/bin/bash</string><string>$REPO/agent_team/run_digest.sh</string></array>
  <key>StartCalendarInterval</key><dict><key>Hour</key><integer>7</integer><key>Minute</key><integer>3</integer></dict>
  <key>RunAtLoad</key><false/>
  <key>StandardOutPath</key><string>$LOGS/launchd-digest.log</string>
  <key>StandardErrorPath</key><string>$LOGS/launchd-digest.err</string>
</dict>
</plist>
EOF

for f in caffeinate worker digest; do
  L="com.marketdaily.agentteam.$f"
  launchctl unload "$DST/$L.plist" 2>/dev/null || true
  launchctl load "$DST/$L.plist"
  echo "✅ 已載入 $L"
done
echo
echo "本機 Agent Team 已啟動(repo: $REPO):"
echo "  · caffeinate — 充電時不讓 Mac 睡眠"
echo "  · worker     — 每 30 分鐘撿一個任務做"
echo "  · digest     — 每天 07:03 寄晨間匯總"
echo
echo "停用:bash agent_team/uninstall_local.sh"
