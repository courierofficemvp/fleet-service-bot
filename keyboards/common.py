from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

mechanic_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Записать сервис")],
        [KeyboardButton(text="⏳ Сервисы в ожидании")],
        [KeyboardButton(text="📌 Мои сервисы")],
    ],
    resize_keyboard=True
)

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Создать сервис")],
        [KeyboardButton(text="📊 Сделанные сервисы")],
    ],
    resize_keyboard=True
)

accountant_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Сделанные сервисы")],
    ],
    resize_keyboard=True
)

def confirm_kb(service_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept:{service_id}"),
            InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel:{service_id}")
        ]
    ])

def complete_kb(service_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔧 Завершить", callback_data=f"finish:{service_id}")
        ]
    ])
