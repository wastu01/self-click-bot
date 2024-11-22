import discord
import logging
import sys
import os
import asyncio
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

# 加載環境變數，覆蓋舊快取
load_dotenv(override=True)

# 定義提前初始化的秒數
INITIALIZE_BEFORE_SEC = int(os.getenv("INITIALIZE_BEFORE_SEC", 10))  # 預設提前 10 秒
TOKEN = os.getenv('USER_TOKEN')
CHANNEL_ID = int(os.getenv('ALLOWED_IDS'))
BONG_BUTTON_ID = os.getenv('BUTTON_ID')

# 配置日誌輸出
log_filename = f"/Users/larry/Github/self-click-bot/cron_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logging.info("Bot script started.")

client = discord.Client()

# 記錄最後的訊息 ID
last_message_id = None

async def check_and_click_button(channel):
    global last_message_id
    try:
        async for message in channel.history(limit=1):  # 獲取最新訊息
            # 訊息的時間與整點時間對比
            message_time = message.created_at.replace(tzinfo=timezone.utc).timestamp()
            scheduled_time = datetime.now(timezone.utc).replace(second=0, microsecond=0).timestamp()

            logging.info(f"Message created at: {message_time}, Scheduled time: {scheduled_time}")

            # 確保訊息是整點後產生
            if message_time < scheduled_time:
                logging.info("Old message detected, skipping...")
                return

            # 如果訊息是新訊息且尚未處理
            if message.id != last_message_id:
                last_message_id = message.id  # 更新最新消息 ID
                logging.info(f"New bot message detected: {message.content}")
                for action_row in message.components:
                    for component in action_row.children:
                        if isinstance(component, discord.Button) and component.custom_id == BONG_BUTTON_ID:
                            logging.info(f"Clicking button with custom_id '{BONG_BUTTON_ID}'.")
                            await asyncio.wait_for(component.click(), timeout=5)
                            logging.info("Button clicked successfully.")
                            return
    except Exception as e:
        logging.error(f"Error while checking messages: {e}")

async def main():
    await client.wait_until_ready()

    # 計算到下一整點的延遲
    current_time = datetime.now(timezone.utc)
    next_minute = (current_time + timedelta(minutes=1)).replace(second=0, microsecond=0)
    delay = (next_minute - current_time).total_seconds() - INITIALIZE_BEFORE_SEC

    # 確保 delay 為正值
    if delay < 0:
        next_minute += timedelta(minutes=1)
        delay = (next_minute - current_time).total_seconds()

    logging.info(f"Current time: {current_time}, Next minute: {next_minute}, Final delay: {delay:.2f} second(s)")
    await asyncio.sleep(delay)

    # 記錄整點檢測開始
    logging.info("Starting detection at the exact scheduled time.")

    # 開始檢測按鈕
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        logging.info(f"Monitoring channel ID: {CHANNEL_ID}")
        await check_and_click_button(channel)
    else:
        logging.error("Channel not found. Check your CHANNEL_ID in .env.")

    # 結束程式
    await client.close()
    logging.info("Bot operation completed.")
    sys.exit(0)

@client.event
async def on_ready():
    logging.info(f"Logged in as {client.user}")
    asyncio.create_task(main())

client.run(TOKEN)
