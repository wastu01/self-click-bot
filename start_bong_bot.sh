#!/bin/bash

# 防止脚本重复运行
if pgrep -f "/Users/larry/Github/self-click-bot/selfbot-click-button.py" > /dev/null; then
    echo "Script is already running. Exiting..." >> /Users/larry/Github/self-click-bot/cron_debug.log
    exit 1
fi

LOCKFILE="/tmp/self-click-bot.lock"

# 检查是否已有锁文件
if [ -e $LOCKFILE ]; then
    echo "Another instance is running. Exiting..." >> /Users/larry/Github/self-click-bot/cron_debug.log
    exit 1
fi

# 创建锁文件
touch $LOCKFILE

# 删除锁文件并执行清理
trap "rm -f $LOCKFILE" EXIT

# 记录脚本启动时间
echo "Script executed at $(date)" >> /Users/larry/Github/self-click-bot/cron_debug.log

# 切换到脚本所在目录
cd /Users/larry/Github/self-click-bot || exit

# 启动 Python 脚本
/Users/larry/Github/self-click-bot/venv/bin/python selfbot-click-button.py >> /Users/larry/Github/self-click-bot/cron_debug.log 2>&1
