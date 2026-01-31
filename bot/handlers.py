from telegram import Update
from telegram.ext import ContextTypes
from bot.monitor import monitor


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(monitor.get_status())
