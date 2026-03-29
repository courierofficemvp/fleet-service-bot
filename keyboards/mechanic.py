from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

mechanic_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⏳ Сервисы в ожидании")],
        [KeyboardButton(text="📌 Мои сервисы")],
    ],
    resize_keyboard=True,
    is_persistent=True
)
