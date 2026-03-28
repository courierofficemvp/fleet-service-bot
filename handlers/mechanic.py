from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.common import confirm_kb, complete_kb
from sheets.pending import get_pending, update_status, get_by_id, delete_pending
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

    services = get_my_completed_since(user_display, msg.text)

    if not services:
        await msg.answer("Нет сервисов")
        await state.clear()
        return

    for s in services:
        await msg.answer(
            f"""📊 ТВОИ СЕРВИСЫ

🚗 {s['car_number']}
🕒 {s['datetime']}
💰 {s['netto']} zł
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
        if s["status"] != "pending":
            continue

        await msg.answer(
            f"""🚗 {s['car_number']}
🕒 {s['datetime']}
📄 {s['work_description']}
""",
            reply_markup=confirm_kb(s["id"])
        )

# ===============================
# ✅ ПРИНЯТЬ
# ===============================

@router.callback_query(lambda c: c.data.startswith("accept:"))
async def accept(callback: CallbackQuery):
    service_id = callback.data.split(":")[1]
    user = get_user_display(callback.from_user)

    service = get_by_id(service_id)

    # 🔥 защита от двойного принятия
    if service["assigned_to"] and service["assigned_to"] != user:
        await callback.answer("Уже взят другим механиком", show_alert=True)
        return

    update_status(service_id, "in_progress", user)

    await callback.message.edit_reply_markup()
    await callback.message.answer("Ты взял сервис", reply_markup=complete_kb(service_id))

# ===============================
# ❌ ОТМЕНА
# ===============================

@router.callback_query(lambda c: c.data.startswith("cancel:"))
async def cancel(callback: CallbackQuery):
    service_id = callback.data.split(":")[1]
    user = get_user_display(callback.from_user)

    service = get_by_id(service_id)

    # 🔥 только владелец может отменить
    if service["assigned_to"] and service["assigned_to"] != user:
        await callback.answer("Это не твой сервис", show_alert=True)
        return

    update_status(service_id, "pending", "")

    await callback.message.edit_reply_markup()
    await callback.answer("Отменено")

# ===============================
# 🔧 ЗАВЕРШЕНИЕ
# ===============================

class FinishService(StatesGroup):
    netto = State()
    comment = State()

@router.callback_query(lambda c: c.data.startswith("finish:"))
async def finish(callback: CallbackQuery, state: FSMContext):
    service_id = callback.data.split(":")[1]
    user = get_user_display(callback.from_user)

    service = get_by_id(service_id)

    # 🔥 только владелец может завершить
    if service["assigned_to"] != user:
        await callback.answer("Это не твой сервис", show_alert=True)
        return

    await state.update_data(service_id=service_id)
    await callback.message.answer("Введите NETTO:")
    await state.set_state(FinishService.netto)

@router.message(FinishService.netto)
async def get_netto(msg: Message, state: FSMContext):
    # 🔥 очистка ввода
    netto = msg.text.replace(",", ".").replace("zł", "").strip()

    try:
        float(netto)
    except:
        await msg.answer("❌ Введите число (например 250 или 250.50)")
        return

    await state.update_data(netto=netto)
    await msg.answer("Комментарий:")
    await state.set_state(FinishService.comment)

@router.message(FinishService.comment)
async def finish_done(msg: Message, state: FSMContext):
    data = await state.get_data()
    service = get_by_id(data["service_id"])
    user = get_user_display(msg.from_user)

    result = {
        "id": service["id"],
        "car_number": service["car_number"],
        "datetime": service["datetime"],
        "netto": data["netto"],
        "comment": msg.text,
        "created_by": service["created_by"],
        "completed_by": user
    }

    add_completed(result)
    delete_pending(service["id"])

    await msg.answer("✅ Сервис завершён")
    await state.clear()
