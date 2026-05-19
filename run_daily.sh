#!/bin/bash
# 財經日報 — 每日自動發送腳本
cd "/Users/delvin/Downloads/Delvin agent"

LOG_DIR="logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/$(date +%Y-%m-%d).log"

echo "=== $(date '+%Y-%m-%d %H:%M:%S') 開始執行 ===" >> "$LOG_FILE"
/usr/bin/python3 main.py >> "$LOG_FILE" 2>&1
echo "=== $(date '+%Y-%m-%d %H:%M:%S') 執行完畢 ===" >> "$LOG_FILE"
