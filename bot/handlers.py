from telegram import Update
from telegram.ext import ContextTypes

from bot.access import USER_IP_MAP
from bot.keyboards import STATUS_KEYBOARD
from bot.registry import monitors


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Натисни кнопку «Статус», щоб подивитись стан.",
        reply_markup=STATUS_KEYBOARD,
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    allowed_ips = USER_IP_MAP.get(user_id)
    if not allowed_ips:
        await update.message.reply_text(
            "❌ У вас немає доступу.",
            reply_markup=STATUS_KEYBOARD,
        )
        return

    parts = []
    for monitor in monitors:
        if monitor.name in allowed_ips:
            parts.append(monitor.get_status())

    await update.message.reply_text("\n\n".join(parts), reply_markup=STATUS_KEYBOARD)
