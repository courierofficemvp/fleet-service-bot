from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.common import confirm_kb, complete_kb
from sheets.pending import get_pending, update_status, get_by_id
from sheets.completed import add_completed, get_my_completed_since
from sheets.users import get_user_display

router = Router()

# ===============================
# 📌 МОИ СЕРВИСЫ
# ===============================

class MyServices(StatesGroup):
    date_from = State()

@router.message(lambda msg: msg.text == "📌 Мои сервисы")
async def my_services_start(msg: Message, state: FSMContext):
    await msg.answer("Введите дату ОТ (DD.MM.YYYY):")
    await state.set_state(MyServices.date_from)

@router.message(MyServices.date_from)
async def my_services_show(msg: Message, state: FSMContext):
    user_display = get_user_display(msg.from_user)

    try:
        services = get_my_completed_since(user_display, msg.text.strip())
    except:
        await msg.answer("❌ Неверный формат даты")
        return

    if not services:
        await msg.answer("Нет сервисов за этот период")
        await state.clear()
        return

    for s in services:
        await msg.answer(
            f"""📊 ТВОИ СЕРВИСЫ

🚗 {s.get('car_number')}
🕒 {s.get('datetime')}
💰 NETTO: {s.get('netto')} zł
💵 BRUTTO: {s.get('brutto')} zł
📝 {s.get('comment')}
"""
        )

    await state.clear()

# ===============================
# ⏳ ОЖИДАЮЩИЕ
# ===============================

@router.message(lambda msg: msg.text == "⏳ Сервисы в ожидании")
async def pending(msg: Message):
    services = get_pending()

    for s in services:
        if s.get("status") != "pending":
            continue

        await msg.answer(
            f"""🚗 {s.get('car_number')}
🕒 {s.get('datetime')}
📄 {s.get('work_description')}
📞 {s.get('driver_phone')}
""",
            reply_markup=confirm_kb(s.get("id"))
        )
