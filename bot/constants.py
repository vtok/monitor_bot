import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID", "0"))

TARGET_IP = os.getenv("TARGET_IP", "8.8.8.8")

PING_INTERVAL = 3
STATE_CONFIRMATION = 15
