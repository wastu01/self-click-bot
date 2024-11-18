import discord
import logging
import sys
import os
import time
from dotenv import load_dotenv
import asyncio
from datetime import datetime

# 强制加载环境变量，覆盖旧缓存
load_dotenv(override=True)

TOKEN = os.getenv('USER_TOKEN')
CHANNEL_ID = int(os.getenv('ALLOWED_IDS'))
BONG_BUTTON_ID = os.getenv('BUTTON_ID')

# 清除所有现有的处理器
for handler in logging.getLogger().handlers[:]:
    logging.getLogger().removeHandler(handler)


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

client = discord.Client()  # 保留原始的 discord.Client() 实例

last_message_id = None  # 记录最后一次的消息

async def check_and_click_button(channel):
    global last_message_id
    try:
        retries = 30  # 最大重试次数
        for attempt in range(retries):
            async for message in channel.history(limit=1):
                if message.author.bot:
                    if message.id == last_message_id:
                        logging.info("No new message detected, skipping...")
                        await asyncio.sleep(0.01)  # 等待  秒后重试
                        continue

                    last_message_id = message.id  # 更新最新消息 ID
                    logging.info(f"New bot message detected: {message.content}")

                    for action_row in message.components:
                        for component in action_row.children:
                            if isinstance(component, discord.Button) and component.custom_id == BONG_BUTTON_ID:
                                logging.info(f"Attempting to click the button with custom_id '{BONG_BUTTON_ID}'.")
                                await asyncio.sleep(0.01)  # 适当延迟
                                await asyncio.wait_for(component.click(), timeout=10)
                                logging.info("Button clicked successfully.")
                                return
                await asyncio.sleep(0.02)  # 若无效消息，延迟重试
    except Exception as e:
        logging.error(f"Error while checking messages: {e}")

async def main():
    await client.wait_until_ready()
    # 手动运行时跳过延迟
    if "MANUAL_RUN" in os.environ:
        logging.info("Manual run detected, skipping delay.")
    else:
        # 等待到整点开始检测
        current_time = time.localtime()
        if current_time.tm_sec < 60:
            delay = 60 - current_time.tm_sec
            await asyncio.sleep(delay)

    channel = client.get_channel(CHANNEL_ID)
    if channel:
        logging.info(f"Monitoring channel ID: {CHANNEL_ID}")
        await asyncio.wait_for(check_and_click_button(channel), timeout=15)
    else:
        logging.error("Channel not found. Check your CHANNEL_ID in .env.")
    await client.close()
    logging.info("Bot operation completed.")
    sys.exit(0)  # 在结束程序时退出

@client.event
async def on_ready():
    logging.info(f"Logged in as {client.user}")
    asyncio.create_task(main())  # 保留原来的调用方式

client.run(TOKEN)
