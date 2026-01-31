from telegram import ReplyKeyboardMarkup, KeyboardButton

STATUS_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("📊 Статус")],
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
    selective=True,
)
