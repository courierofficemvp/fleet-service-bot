from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import logging
import uuid

from sheets.pending import add_pending
from sheets.users import get_users_by_role, get_user_display
from sheets.flota import car_exists
from keyboards.common import confirm_kb
from services.validation import validate_datetime

router = Router()


class CreateService(StatesGroup):
    car = State()
    dt = State()
    work = State()
    phone = State()


@router.message(lambda msg: msg.text == "➕ Создать сервис")
async def start_create(msg: Message, state: FSMContext):
    await msg.answer("Номер авто:")
    await state.set_state(CreateService.car)


@router.message(CreateService.car)
async def car(msg: Message, state: FSMContext):
    car_number = (msg.text or "").upper().strip()

    if not car_exists(car_number):
        await msg.answer("❌ Неправильный номер автомобиля")
        return

    await state.update_data(car_number=car_number)
    await msg.answer("Дата (DD.MM.YYYY HH:mm):")
    await state.set_state(CreateService.dt)


@router.message(CreateService.dt)
async def dt(msg: Message, state: FSMContext):
    dt_value = (msg.text or "").strip()

    if not validate_datetime(dt_value):
        await msg.answer("❌ Неверный формат даты. Пример: 30.03.2026 14:30")
        return

    await state.update_data(datetime=dt_value)
    await msg.answer("Описание работ:")
    await state.set_state(CreateService.work)


@router.message(CreateService.work)
async def work(msg: Message, state: FSMContext):
    work_value = (msg.text or "").strip()

    if not work_value:
        await msg.answer("❌ Описание работ не может быть пустым")
        return

    await state.update_data(work_description=work_value)
    await msg.answer("Телефон водителя:")
    await state.set_state(CreateService.phone)


@router.message(CreateService.phone)
async def phone(msg: Message, state: FSMContext):
    phone_value = (msg.text or "").strip()

    if not phone_value:
        await msg.answer("❌ Телефон не может быть пустым")
        return

    data = await state.get_data()
    data["driver_phone"] = phone_value
    data["id"] = str(uuid.uuid4())
    data["created_by"] = get_user_display(msg.from_user)

    saved_id = add_pending(data)

    mechanics = get_users_by_role("mechanic")

    text = f"""🚗 Новый сервис

ID: {saved_id}
Авто: {data['car_number']}
Дата: {data['datetime']}
Работы: {data['work_description']}
Телефон: {data['driver_phone']}
Кто записал: {data['created_by']}
"""

    for mechanic_id in mechanics:
        try:
            await msg.bot.send_message(
                chat_id=int(mechanic_id),
                text=text,
                reply_markup=confirm_kb(saved_id)
            )
        except Exception as e:
            logging.exception("Failed to send service to mechanic_id=%s: %s", mechanic_id, e)

    await msg.answer("✅ Сервис отправлен механику")
    await state.clear()
