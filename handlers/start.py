from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from services.roles import check_role
from keyboards.common import mechanic_kb, admin_kb, accountant_kb

router = Router()

@router.message(Command("start"))
async def start(msg: Message):
    role = check_role(msg.from_user.id)

    if not role:
        await msg.answer("❌ У вас нет доступа")
        return

    await msg.answer(f"DEBUG ROLE: {role}")

    if role == "mechanic":
        await msg.answer("Меню", reply_markup=mechanic_kb)

    elif role in ["admin", "assistant"]:
        await msg.answer("Меню", reply_markup=admin_kb)

    elif role in ["accountant", "chief_mechanic"]:
        await msg.answer("Меню", reply_markup=accountant_kb)

    else:
        await msg.answer("❌ Роль не определена")
