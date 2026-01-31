import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler

from bot.monitor import monitor
from bot.handlers import status_command
from bot.constants import BOT_TOKEN


async def post_init(app):
    asyncio.create_task(monitor.run(app))


def main():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("status", status_command))
    app.run_polling()


if __name__ == "__main__":
    main()
