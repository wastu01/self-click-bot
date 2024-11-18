# Self-Click-Bot

## Overview
this self-bot project to automate button clicking tasks in Discord. The bot is designed to interact with specific Discord messages and components, aiming to achieve high precision in timed tasks like clicking buttons.

## Features
- Automatically detects the latest bot message.
- Clicks a specific button based on the `custom_id`.

## Usage
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/self-click-bot.git
   ```

## Environment Variables
Create a `.env` file in the project directory with the following content:

```env
# channel ids where the bot listens for messages
ALLOWED_IDS=xxx

BONG_BUTTON_ID=xxx

USER_TOKEN=xxx
```

## Setup
1. Clone the repository:
   ```bash
   git clone <repository_url>
   ```
2. Navigate to the project directory:
   ```bash
   cd Sudo-bot
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Configure environment variables in a `.env` file:
   - `USER_TOKEN`: Your Discord user token.
   - `ALLOWED_IDS`: The Discord channel ID to monitor.
   - `BONG_BUTTON_ID`: The custom ID of the target button.

6. Test the bot locally:
   ```bash
   python selfbot-click-buttom.py
   ```

## Cron Setup on Mac
To automate the bot's execution:
1. Edit the `crontab` configuration:
   ```bash
   crontab -e
   ```
2. Add the following line for testing (adjust timing as needed):
   ```bash
   * * * * * /path/to/start_bong_bot.sh
   ```

## License
This project is for educational and personal use only. Use responsibly.
