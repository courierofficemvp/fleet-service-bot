from aiogram import Router
from aiogram.types import Message

from services.roles import check_role
from keyboards.mechanic import mechanic_kb

router = Router()


@router.message()
async def start(message: Message):
    role = check_role(message.from_user)

    if role == "mechanic":
        await message.answer(
            "👨‍🔧 Вы вошли как механик",
            reply_markup=mechanic_kb
        )
        return

    await message.answer("У вас нет доступа")
