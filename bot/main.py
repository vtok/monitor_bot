import asyncio

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from bot.config import IP_MONITORING
from bot.constants import BOT_TOKEN
from bot.handlers import status_command, start_command
from bot.registry import monitors


async def notify(app, ip_name: str, text: str):
    members = IP_MONITORING[ip_name]["members"]
    for chat_id in members:
        await app.bot.send_message(chat_id=chat_id, text=text)


async def post_init(app):
    for monitor in monitors:
        asyncio.create_task(monitor.run(lambda ip, msg: notify(app, ip, msg)))


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("status", status_command))

    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^📊 Статус$"), status_command))

    app.run_polling()


if __name__ == "__main__":
    main()
