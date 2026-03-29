from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from services.roles import check_role
from keyboards.mechanic import mechanic_kb

router = Router()


def get_role_safe(user):
    try:
        return check_role(user)
    except Exception as e:
        print("ROLE ERROR:", e)
        return None


# 🔥 ПРАВИЛЬНЫЙ /start
@router.message(Command("start"))
async def start_cmd(message: Message):
    role = get_role_safe(message.from_user)

    # DEBUG
    await message.answer(f"ROLE: {role}")

    if role == "mechanic":
        await message.answer(
            "👨‍🔧 Вы механик",
            reply_markup=mechanic_kb
        )
        return

    await message.answer("Нет доступа")


# 🔥 ПРАВИЛЬНЫЙ /menu
@router.message(Command("menu"))
async def menu_cmd(message: Message):
    role = get_role_safe(message.from_user)

    if role == "mechanic":
        await message.answer(
            "📋 Меню механика",
            reply_markup=mechanic_kb
        )
        return

    await message.answer("Нет доступа")
