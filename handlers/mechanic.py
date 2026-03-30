from datetime import datetime

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from keyboards.common import complete_kb, confirm_kb
from sheets.completed import add_completed, exists_completed, get_my_completed_since
from sheets.pending import assign_if_free, delete_pending, get_by_id, get_pending, update_status
from sheets.users import get_user_display
from sheets.flota import car_exists
from services.validation import validate_datetime

router = Router()


class AddService(StatesGroup):
    car = State()
    dt = State()
    netto = State()
    comment = State()


class MyServices(StatesGroup):
    date_from = State()


class FinishService(StatesGroup):
    netto = State()
    comment = State()


def normalize_money(value: str) -> float:
    text = str(value or "").replace(",", ".").replace("zł", "").strip()
    return float(text)


@router.message(lambda msg: msg.text == "➕ Записать сервис")
async def start(msg: Message, state: FSMContext):
    await msg.answer("Введите номер авто:")
    await state.set_state(AddService.car)


@router.message(AddService.car)
async def car(msg: Message, state: FSMContext):
    car_number = (msg.text or "").upper().strip()

    if not car_exists(car_number):
        await msg.answer("❌ Неправильный номер автомобиля")
        return

    await state.update_data(car_number=car_number)
    await msg.answer("Дата (DD.MM.YYYY HH:mm):")
    await state.set_state(AddService.dt)


@router.message(AddService.dt)
async def dt(msg: Message, state: FSMContext):
    dt_value = (msg.text or "").strip()

    if not validate_datetime(dt_value):
        await msg.answer("❌ Неверный формат даты. Пример: 30.03.2026 14:30")
        return

    await state.update_data(datetime=dt_value)
    await msg.answer("NETTO:")
    await state.set_state(AddService.netto)


@router.message(AddService.netto)
async def netto(msg: Message, state: FSMContext):
    try:
        netto_value = normalize_money(msg.text)
        if netto_value < 0:
            raise ValueError
    except Exception:
        await msg.answer("❌ Неверная сумма")
        return

    await state.update_data(netto=f"{netto_value:.2f}")
    await msg.answer("Комментарий:")
    await state.set_state(AddService.comment)


@router.message(AddService.comment)
async def comment(msg: Message, state: FSMContext):
    data = await state.get_data()
    user_display = get_user_display(msg.from_user)

    service_id = f"manual-{msg.from_user.id}-{int(datetime.now().timestamp())}"

    result = {
        "id": service_id,
        "car_number": data["car_number"],
        "datetime": data["datetime"],
        "netto": data["netto"],
        "comment": (msg.text or "").strip(),
        "created_by": user_display,
        "completed_by": user_display,
    }

    created = add_completed(result)

    if not created:
        await msg.answer("❌ Не удалось добавить сервис")
        await state.clear()
        return

    await msg.answer("✅ Сервис добавлен")
    await state.clear()


@router.message(lambda msg: msg.text == "📌 Мои сервисы")
async def my_services_start(msg: Message, state: FSMContext):
    await msg.answer("Введите дату ОТ (DD.MM.YYYY):")
    await state.set_state(MyServices.date_from)


@router.message(MyServices.date_from)
async def my_services_show(msg: Message, state: FSMContext):
    raw_date = (msg.text or "").strip()

    try:
        datetime.strptime(raw_date, "%d.%m.%Y")
    except ValueError:
        await msg.answer("❌ Формат даты: DD.MM.YYYY")
        return

    user_display = get_user_display(msg.from_user)
    services = get_my_completed_since(user_display, raw_date)

    if not services:
        await msg.answer("Нет сервисов")
        await state.clear()
        return

    for s in services:
        await msg.answer(
            f"""📊 ТВОИ СЕРВИСЫ

🚗 {s.get('car_number', '-')}
🕒 {s.get('datetime', '-')}
💰 {s.get('netto', '-')} zł
📝 {s.get('comment', '-')}
"""
        )

    await state.clear()


@router.message(lambda msg: msg.text == "⏳ Сервисы в ожидании")
async def pending(msg: Message):
    services = get_pending()
    pending_services = [s for s in services if s.get("status") == "pending"]

    if not pending_services:
        await msg.answer("Нет сервисов в ожидании")
        return

    for s in pending_services:
        await msg.answer(
            f"""🚗 {s.get('car_number', '-')}
🕒 {s.get('datetime', '-')}
📄 {s.get('work_description', '-')}
📞 {s.get('driver_phone', '-')}
""",
            reply_markup=confirm_kb(s["id"])
        )


@router.callback_query(lambda c: c.data and c.data.startswith("accept:"))
async def accept(callback: CallbackQuery):
    service_id = callback.data.split(":", 1)[1]
    user = get_user_display(callback.from_user)

    success = assign_if_free(service_id, user)

    if not success:
        await callback.answer("Уже взят другим механиком или недоступен", show_alert=True)
        return

    await callback.answer("Сервис принят")
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        "Ты взял сервис",
        reply_markup=complete_kb(service_id)
    )


@router.callback_query(lambda c: c.data and c.data.startswith("cancel:"))
async def cancel(callback: CallbackQuery):
    service_id = callback.data.split(":", 1)[1]
    user = get_user_display(callback.from_user)

    service = get_by_id(service_id)

    if not service:
        await callback.answer("Сервис не найден", show_alert=True)
        return

    if service.get("assigned_to") != user:
        await callback.answer("Это не твой сервис", show_alert=True)
        return

    if service.get("status") != "in_progress":
        await callback.answer("Нельзя отменить этот сервис", show_alert=True)
        return

    update_status(service_id, "pending", "")
    await callback.answer("Отменено")
    await callback.message.edit_reply_markup()


@router.callback_query(lambda c: c.data and c.data.startswith("finish:"))
async def finish(callback: CallbackQuery, state: FSMContext):
    service_id = callback.data.split(":", 1)[1]
    user = get_user_display(callback.from_user)

    service = get_by_id(service_id)

    if not service:
        await callback.answer("Сервис не найден", show_alert=True)
        return

    if service.get("assigned_to") != user:
        await callback.answer("Это не твой сервис", show_alert=True)
        return

    if service.get("status") != "in_progress":
        await callback.answer("Сервис не в работе", show_alert=True)
        return

    if exists_completed(service_id):
        await callback.answer("Сервис уже завершён", show_alert=True)
        return

    await state.update_data(service_id=service_id)
    await callback.answer()
    await callback.message.answer("Введите NETTO:")
    await state.set_state(FinishService.netto)


@router.message(FinishService.netto)
async def get_netto(msg: Message, state: FSMContext):
    raw_value = (msg.text or "").replace(",", ".").replace("zł", "").strip()

    try:
        netto_value = float(raw_value)
        if netto_value < 0:
            raise ValueError
    except ValueError:
        await msg.answer("❌ Введите корректное число (например 250 или 250.50)")
        return

    await state.update_data(netto=f"{netto_value:.2f}")
    await msg.answer("Комментарий:")
    await state.set_state(FinishService.comment)


@router.message(FinishService.comment)
async def finish_done(msg: Message, state: FSMContext):
    data = await state.get_data()
    service_id = data.get("service_id")

    if not service_id:
        await msg.answer("❌ Потерян ID сервиса")
        await state.clear()
        return

    service = get_by_id(service_id)
    user = get_user_display(msg.from_user)

    if not service:
        await msg.answer("❌ Сервис не найден")
        await state.clear()
        return

    if service.get("assigned_to") != user:
        await msg.answer("❌ Это не твой сервис")
        await state.clear()
        return

    if service.get("status") != "in_progress":
        await msg.answer("⚠️ Сервис уже не активен")
        await state.clear()
        return

    if exists_completed(service_id):
        await msg.answer("⚠️ Сервис уже завершён ранее")
        await state.clear()
        return

    result = {
        "id": service["id"],
        "car_number": service.get("car_number", ""),
        "datetime": service.get("datetime", ""),
        "netto": data["netto"],
        "comment": (msg.text or "").strip(),
        "created_by": service.get("created_by", ""),
        "completed_by": user,
    }

    created = add_completed(result)
    if not created:
        await msg.answer("❌ Не удалось завершить сервис")
        await state.clear()
        return

    deleted = delete_pending(service_id)
    if not deleted:
        await msg.answer("⚠️ Сервис записан в completed, но не удалён из pending")
        await state.clear()
        return

    await msg.answer("✅ Сервис завершён")
    await state.clear()
