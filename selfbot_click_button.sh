#!/bin/bash
# 簡化版的 Discord 自動點擊 Bot 啟動腳本（無外部 log）

PROJECT_DIR="/Users/larry/Github/self-click-bot"
PYTHON="$PROJECT_DIR/venv/bin/python"
SCRIPT="$PROJECT_DIR/selfbot_click_button.py"

cd "$PROJECT_DIR" || exit 1

# 執行腳本但不留下任何輸出
"$PYTHON" "$SCRIPT" > /dev/null 2>&1
