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

    # 🔧 mechanic — только его меню
    if role == "mechanic":
        await msg.answer("Меню", reply_markup=mechanic_kb)

    # 👑 admin — полный доступ
    elif role == "admin":
        await msg.answer("Меню", reply_markup=admin_kb)

    # 👩‍💼 assistant — как admin (создание + отчёт)
    elif role == "assistant":
        await msg.answer("Меню", reply_markup=admin_kb)

    # 🧠 chief_mechanic — записи + отчёты
    elif role == "chief_mechanic":
        await msg.answer("Меню", reply_markup=mechanic_kb)
        await msg.answer("Дополнительно доступен отчёт", reply_markup=accountant_kb)

    # 💰 accountant — только отчёты
    elif role == "accountant":
        await msg.answer("Меню", reply_markup=accountant_kb)

    else:
        await msg.answer("❌ Роль не определена")
