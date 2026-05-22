#!/bin/zsh
# update_stocks.sh — 每月自動更新股票資料庫並部署
set -e

PROJECT_DIR="/Users/delvin/Downloads/Delvin agent"
LOG="$PROJECT_DIR/update_stocks.log"

echo "[$(date '+%Y-%m-%d %H:%M')] 開始更新股票資料庫..." >> "$LOG"

cd "$PROJECT_DIR"
python3 fetch_stocks.py >> "$LOG" 2>&1

cd "$PROJECT_DIR"
npx wrangler pages deploy docs --project-name marketdaily --commit-dirty=true >> "$LOG" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M')] 完成" >> "$LOG"
