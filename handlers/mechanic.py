from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from sheets.completed import add_completed
from sheets.pending import get_pending, delete_pending, get_by_id, update_status
from sheets.flota import car_exists
from sheets.users import get_user_display
from keyboards.common import complete_kb

router = Router()

class AddService(StatesGroup):
    car = State()
    dt = State()
    netto = State()
    comment = State()

class FinishService(StatesGroup):
    netto = State()
    comment = State()
    service_id = State()

def normalize_money(value: str):
    return float(value.replace(",", ".").strip())


# ===============================
# ➕ РУЧНОЕ ДОБАВЛЕНИЕ СЕРВИСА
# ===============================

@router.message(lambda msg: msg.text == "➕ Записать сервис")
async def start(msg: Message, state: FSMContext):
    await msg.answer("Введите номер авто:")
    await state.set_state(AddService.car)

@router.message(AddService.car)
async def car(msg: Message, state: FSMContext):
    car_number = msg.text.upper().strip()

    if not car_exists(car_number):
        await msg.answer("❌ Неправильный номер автомобиля")
        return

    await state.update_data(car_number=car_number)
    await msg.answer("Дата (DD.MM.YYYY HH:mm):")
    await state.set_state(AddService.dt)

@router.message(AddService.dt)
async def dt(msg: Message, state: FSMContext):
    await state.update_data(datetime=msg.text.strip())
    await msg.answer("NETTO:")
    await state.set_state(AddService.netto)

@router.message(AddService.netto)
async def netto(msg: Message, state: FSMContext):
    try:
        netto_value = normalize_money(msg.text)
    except:
        await msg.answer("❌ Неверная сумма")
        return

    await state.update_data(netto=netto_value)
    await msg.answer("Комментарий:")
    await state.set_state(AddService.comment)

@router.message(AddService.comment)
async def comment(msg: Message, state: FSMContext):
    data = await state.get_data()
    user_display = get_user_display(msg.from_user)

    result = {
        "car_number": data["car_number"],
        "datetime": data["datetime"],
        "netto": data["netto"],
        "comment": msg.text.strip(),
        "created_by": user_display,
        "completed_by": user_display
    }

    add_completed(result)

    await msg.answer("✅ Сервис добавлен вручную")
    await state.clear()


# ===============================
# ⏳ СПИСОК ОЖИДАЮЩИХ
# ===============================

@router.message(lambda msg: msg.text == "⏳ Сервисы в ожидании")
async def pending_list(msg: Message):
    services = get_pending()

    if not services:
        await msg.answer("Нет сервисов")
        return

    for s in services:
        await msg.answer(
            f"""🚗 {s.get('car_number')}
🕒 {s.get('datetime')}
📄 {s.get('work_description')}
📞 {s.get('driver_phone')}
👤 {s.get('created_by')}
""",
            reply_markup=complete_kb(s.get("id"))
        )


# ===============================
# ✅ ПРИНЯТЬ
# ===============================

@router.callback_query(F.data.startswith("accept:"))
async def accept(cb: CallbackQuery):
    service_id = cb.data.split(":")[1]

    service = get_by_id(service_id)

    if not service:
        await cb.answer("❌ Сервис не найден", show_alert=True)
        return

    if service.get("status") != "pending":
        await cb.answer("❌ Уже взят другим механиком", show_alert=True)
        return

    user_display = get_user_display(cb.from_user)

    update_status(service_id, "in_progress", user_display)

    await cb.message.answer(
        f"✅ Ты взял сервис\n👨‍🔧 {user_display}",
        reply_markup=complete_kb(service_id)
    )

    await cb.answer()


# ===============================
# ❌ ОТМЕНА (запрещена если уже взят)
# ===============================

@router.callback_query(F.data.startswith("cancel:"))
async def cancel(cb: CallbackQuery):
    service_id = cb.data.split(":")[1]

    service = get_by_id(service_id)

    if not service:
        await cb.answer("❌ Сервис не найден", show_alert=True)
        return

    if service.get("status") != "pending":
        await cb.answer("❌ Нельзя отменить — сервис уже принят", show_alert=True)
        return

    delete_pending(service_id)

    await cb.message.answer("❌ Сервис отменён")
    await cb.answer()


# ===============================
# 🔧 ЗАВЕРШЕНИЕ (ТОЛЬКО ТЕМ КТО ВЗЯЛ)
# ===============================

@router.callback_query(F.data.startswith("finish:"))
async def finish_start(cb: CallbackQuery, state: FSMContext):
    service_id = cb.data.split(":")[1]

    service = get_by_id(service_id)

    user_display = get_user_display(cb.from_user)

    # 🔥 ПРОВЕРКА КТО ВЗЯЛ
    if service.get("assigned_to") != user_display:
        await cb.answer("❌ Этот сервис взял другой механик", show_alert=True)
        return

    await state.update_data(service_id=service_id)
    await cb.message.answer("NETTO:")
    await state.set_state(FinishService.netto)
    await cb.answer()


@router.message(FinishService.netto)
async def get_netto(msg: Message, state: FSMContext):
    netto = normalize_money(msg.text)
    await state.update_data(netto=netto)
    await msg.answer("Комментарий:")
    await state.set_state(FinishService.comment)


@router.message(FinishService.comment)
async def finish_done(msg: Message, state: FSMContext):
    data = await state.get_data()
    service = get_by_id(data["service_id"])

    result = {
        "car_number": service["car_number"],
        "datetime": service["datetime"],
        "netto": data["netto"],
        "comment": msg.text.strip(),
        "created_by": service.get("created_by", ""),
        "completed_by": get_user_display(msg.from_user)
    }

    add_completed(result)
    delete_pending(data["service_id"])

    await msg.answer("✅ Сервис завершён")
    await state.clear()
