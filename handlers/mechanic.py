from datetime import datetime

from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards.common import confirm_kb, complete_kb
from sheets.pending import get_pending, update_status, get_by_id, delete_pending, assign_if_free
from sheets.completed import add_completed, get_my_completed_since, exists_completed

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
    try:
        datetime.strptime(msg.text, "%d.%m.%Y")
    except:
        await msg.answer("❌ Формат даты: DD.MM.YYYY")
        return

    user_id = str(msg.from_user.id)
    services = get_my_completed_since(user_id, msg.text)

    if not services:
        await msg.answer("Нет сервисов")
        await state.clear()
        return

    for s in services:
        await msg.answer(
            f"""📊 ТВОИ СЕРВИСЫ

🚗 {s.get('car_number')}
🕒 {s.get('datetime')}
💰 {s.get('netto')} zł
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
""",
            reply_markup=confirm_kb(s["id"])
        )


# ===============================
# ✅ ПРИНЯТЬ
# ===============================

@router.callback_query(lambda c: c.data.startswith("accept:"))
async def accept(callback: CallbackQuery):
    service_id = callback.data.split(":")[1]
    user_id = str(callback.from_user.id)

    success = assign_if_free(service_id, user_id)

    if not success:
        await callback.answer("Уже взят или недоступен", show_alert=True)
        return

    await callback.answer("Принято")
    await callback.message.edit_reply_markup()
    await callback.message.answer("Ты взял сервис", reply_markup=complete_kb(service_id))


# ===============================
# ❌ ОТМЕНА
# ===============================

@router.callback_query(lambda c: c.data.startswith("cancel:"))
async def cancel(callback: CallbackQuery):
    service_id = callback.data.split(":")[1]
    user_id = str(callback.from_user.id)

    service = get_by_id(service_id)

    if not service:
        await callback.answer("Не найдено", show_alert=True)
        return

    if service.get("assigned_to") != user_id:
        await callback.answer("Не твой сервис", show_alert=True)
        return

    if service.get("status") != "in_progress":
        await callback.answer("Нельзя отменить", show_alert=True)
        return

    update_status(service_id, "pending", "")

    await callback.answer("Отменено")
    await callback.message.edit_reply_markup()


# ===============================
# 🔧 ЗАВЕРШЕНИЕ
# ===============================

class FinishService(StatesGroup):
    netto = State()
    comment = State()


@router.callback_query(lambda c: c.data.startswith("finish:"))
async def finish(callback: CallbackQuery, state: FSMContext):
    service_id = callback.data.split(":")[1]
    user_id = str(callback.from_user.id)

    service = get_by_id(service_id)

    if not service:
        await callback.answer("Не найдено", show_alert=True)
        return

    if service.get("assigned_to") != user_id:
        await callback.answer("Не твой сервис", show_alert=True)
        return

    if service.get("status") != "in_progress":
        await callback.answer("Не в работе", show_alert=True)
        return

    if exists_completed(service_id):
        await callback.answer("Уже завершено", show_alert=True)
        return

    await state.update_data(service_id=service_id)
    await callback.answer()
    await callback.message.answer("Введите NETTO:")
    await state.set_state(FinishService.netto)


@router.message(FinishService.netto)
async def get_netto(msg: Message, state: FSMContext):
    netto = msg.text.replace(",", ".").replace("zł", "").strip()

    try:
        netto = float(netto)
    except:
        await msg.answer("❌ Введите число")
        return

    await state.update_data(netto=str(netto))
    await msg.answer("Комментарий:")
    await state.set_state(FinishService.comment)


@router.message(FinishService.comment)
async def finish_done(msg: Message, state: FSMContext):
    data = await state.get_data()
    service_id = data.get("service_id")

    service = get_by_id(service_id)
    user_id = str(msg.from_user.id)

    if not service:
        await msg.answer("Ошибка")
        await state.clear()
        return

    if service.get("assigned_to") != user_id:
        await msg.answer("Не твой сервис")
        await state.clear()
        return

    if service.get("status") != "in_progress":
        await msg.answer("Уже закрыт")
        await state.clear()
        return

    if exists_completed(service_id):
        await msg.answer("Уже завершено")
        await state.clear()
        return

    result = {
        "id": service["id"],
        "car_number": service.get("car_number"),
        "datetime": service.get("datetime"),
        "netto": data["netto"],
        "comment": msg.text,
        "created_by": service.get("created_by"),
        "completed_by": user_id
    }

    add_completed(result)
    delete_pending(service["id"])

    await msg.answer("✅ Готово")
    await state.clear()
