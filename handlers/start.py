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

    print(f"DEBUG ROLE: {role}")

    # 👇 МЕХАНИК
    if role == "mechanic":
        await msg.answer("Меню", reply_markup=mechanic_kb)

    # 👇 АДМИН
    elif role == "admin":
        await msg.answer("Меню", reply_markup=admin_kb)

    # 👇 ASSISTANT и ACCOUNTANT — ТОЛЬКО ОТЧЕТЫ
    elif role in ["assistant", "accountant", "chief_mechanic"]:
        await msg.answer("Меню", reply_markup=accountant_kb)

    else:
        await msg.answer("❌ Роль не определена")
