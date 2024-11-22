import discord
import logging
import sys
import os
import time
import asyncio
from dotenv import load_dotenv
from datetime import datetime, timezone

# 加載環境變數，覆蓋舊快取
load_dotenv(override=True)

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
        retries = 10  # 增加重試次數
        for attempt in range(retries):
            async for message in channel.history(limit=1):  # 獲取最新訊息
                # 訊息的時間與當前時間對比
                message_time = message.created_at.replace(tzinfo=timezone.utc).timestamp()
                current_time = datetime.now(timezone.utc).timestamp()

                # 檢查是否為超過一小時的舊訊息
                if current_time - message_time > 3600:  # 超過1小時
                    logging.info("Message is older than one hour, skipping...")
                    await asyncio.sleep(0.005)  # 等待後重試
                    continue

                # 檢查是否為新訊息
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

            logging.info(f"Attempt {attempt + 1}/{retries} failed. Retrying...")
            await asyncio.sleep(0.05)  # 每次重試間隔 50 毫秒
    except Exception as e:
        logging.error(f"Error while checking messages: {e}")

async def main():
    await client.wait_until_ready()

    # 等待至整點，考慮程式啟動時間
    current_time = time.localtime()
    if current_time.tm_sec < 50:  # 確保在整點前幾秒開始檢測
        delay = 50 - current_time.tm_sec
        logging.info(f"Waiting {delay} second(s) to start detection.")
        await asyncio.sleep(delay)

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