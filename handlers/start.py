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
        await msg.answer("⛔ Нет доступа")
        return

    if role == "mechanic":
        await msg.answer("Меню механика", reply_markup=mechanic_kb())

    elif role in ["admin", "assistant", "chief_mechanic"]:
        await msg.answer("Меню", reply_markup=admin_kb())

    elif role == "accountant":
        await msg.answer("Меню бухгалтера", reply_markup=accountant_kb())
