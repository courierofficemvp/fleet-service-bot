from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from keyboards.common import mechanic_kb, admin_kb, accountant_kb

router = Router()

@router.message(Command("start"))
async def start(msg: Message):
    # 🔥 ПОЛНЫЙ BYPASS — ВСЕГДА ADMIN
    await msg.answer("DEBUG: ты зашёл как ADMIN")
    await msg.answer("Меню", reply_markup=admin_kb())
