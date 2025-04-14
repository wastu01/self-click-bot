#!/usr/bin/env python3
"""
自動點擊 Discord Bot 按鈕（以「每小時 00 分」為整點）
----------------------------------------------------------------
流程：
  1. 腳本啟動後，計算距離「下一個整點 HH:00」還有多久，
     先睡到 (整點 - INITIALIZE_BEFORE_SEC) 再初始化。
  2. 整點一到就抓指定頻道最新訊息，若訊息時間在
     (當前整點 - 1 小時) 之後，且包含目標按鈕，就點擊。
  3. 點擊完立即結束，方便用 crontab 每小時排程。
環境變數 (.env)：
  USER_TOKEN              Discord 使用者 Token
  ALLOWED_IDS             目標文字頻道 ID
  BUTTON_ID               目標按鈕 custom_id
  INITIALIZE_BEFORE_SEC   提前初始化秒數(預設 10)
"""

import discord
import logging
import sys
import os
import asyncio
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

# ---------- 讀取 .env ----------
load_dotenv(override=True)

# ---------- 基本設定 ----------
INITIALIZE_BEFORE_SEC: int = int(os.getenv("INITIALIZE_BEFORE_SEC", 2))
TOKEN: str = os.getenv("USER_TOKEN")
CHANNEL_ID: int = int(os.getenv("ALLOWED_IDS"))
BONG_BUTTON_ID: str = os.getenv("BUTTON_ID")

# ---------- 日誌 ----------
log_filename = f"/Users/larry/Github/self-click-bot/cron_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logging.info("▶️ 自動點擊腳本啟動")

# ---------- Discord Client ----------
client = discord.Client()

# 避免重複處理同一則訊息
last_message_id: int | None = None


# async def find_and_click_previous_button(channel):
#     async for message in channel.history(limit=1):
#         for row in message.components:
#             for component in row.children:
#                 if (
#                     isinstance(component, discord.Button)
#                     and component.custom_id == BONG_BUTTON_ID
#                     and not component.disabled
#                 ):
#                     logging.info(f"找到按鈕 custom_id='{component.custom_id}'，準備點擊")
#                     await asyncio.wait_for(component.click(), timeout=5)
#                     logging.info("✅ 前一個按鈕點擊完成")
#                     return
#     logging.info("⚠️ 沒有找到可點擊的按鈕")


async def check_and_click_button(channel: discord.TextChannel) -> None:
    """抓最新訊息，符合條件就點擊按鈕"""
    global last_message_id
    try:
        async for message in channel.history(limit=1):  # 只抓最新一則
            message_time = message.created_at.replace(tzinfo=timezone.utc).timestamp()

            # 取得「當前整點」時間戳（HH:00:00）
            current_hour_start = datetime.now(timezone.utc).replace(
                minute=0, second=0, microsecond=0
            ).timestamp()

            # one_hour_ago = current_hour_start - 3600  # 整點前一小時

            # 時間窗判斷
            if message_time < current_hour_start - 3600:
                logging.info("訊息過於陳舊，略過")
                return

            # 避免重複點
            if message.id == last_message_id:
                # logging.info("已處理過此訊息，略過")
                return
            last_message_id = message.id

            # 尋找按鈕
            for row in message.components:
                for component in row.children:
                    if (
                        isinstance(component, discord.Button)
                        and component.custom_id == BONG_BUTTON_ID
                        and not component.disabled
                    ):
                        logging.info(f"點擊按鈕 custom_id='{BONG_BUTTON_ID}'")
                        await asyncio.wait_for(component.click(), timeout=0.1)
                        logging.info("✅ 按鈕點擊完成")
                        return
            logging.info("⚠️ 找不到可點擊的目標按鈕")
    except Exception as e:
        logging.error(f"檢查或點擊時發生錯誤: {e}")


async def main() -> None:
    """主流程：等待下一整點 → 檢查並點擊"""
    await client.wait_until_ready()

    # ---------- 計算距離下一個「HH:00」的秒數 ----------
    now = datetime.now(timezone.utc)
    next_hour = (now + timedelta(hours=1)).replace(
        minute=0, second=0, microsecond=0
    )
    delay_to_hour = (next_hour - now).total_seconds()

    # 提前 INITIALIZE_BEFORE_SEC 秒初始化
    delay_to_initialize = max(delay_to_hour - INITIALIZE_BEFORE_SEC, 0)

    logging.info(
        f"現在時間: {now}, 下一整點: {next_hour}, "
        f"先睡 {delay_to_initialize:.2f}s 再初始化"
    )

    await asyncio.sleep(delay_to_initialize)

    # 等到整點
    logging.info("等待整點開始快速點擊")
    for _ in range(30):  # 嘗試點擊  n 次
        await check_and_click_button(client.get_channel(CHANNEL_ID))
        await asyncio.sleep(0.6)
    
    # 測試直接點擊前一則按鈕
    # channel = client.get_channel(CHANNEL_ID)
    # if channel is None:
    #     logging.error("❌ 找不到頻道，請確認 ALLOWED_IDS 是否正確")
    #     return
    # await find_and_click_previous_button(channel)
    # ---------- 結束 ----------
    logging.info("🚪 任務完成，準備離線")
    await client.close()
    logging.info("✅ 與 Discord 連線已關閉，程式即將退出")
    return




@client.event
async def on_ready() -> None:
    logging.info(f"✅ 已登入 Discord 使用者: {client.user}")
    asyncio.create_task(main())


# ---------- 進入點 ----------
if __name__ == "__main__":
    try:
        client.run(TOKEN)
    except KeyboardInterrupt:
        logging.info("程序被中斷，清理後退出")
    except Exception as exc:
        logging.error(f"未預期的錯誤: {exc}")
        sys.exit(1)
    else:
        logging.info("程序正常結束")
        sys.exit(0)
