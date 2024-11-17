#!/bin/bash

# 防止腳本重複運行
if pgrep -f "selfbot-click-buttom.py" > /dev/null; then
    echo "Script is already running. Exiting..." >> cron_debug.log
    exit 1
fi

# 記錄啟動時間
echo "start_bong_bot.sh executed at $(date)" >> cron_debug.log

# 執行 Python 腳本，限制運行時間為 50 秒
timeout 20 /venv/bin/python selfbot-click-buttom.py >> cron_debug.log 2>&1