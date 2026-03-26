from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from sheets.pending import add_pending
from sheets.users import get_users_by_role
from sheets.flota import car_exists
from keyboards.common import confirm_kb

import uuid

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
    car_number = msg.text.upper().strip()

    if not car_exists(car_number):
        await msg.answer("❌ Неправильный номер автомобиля")
        return

    await state.update_data(car_number=car_number)
    await msg.answer("Дата (DD.MM.YYYY HH:mm):")
    await state.set_state(CreateService.dt)

@router.message(CreateService.dt)
async def dt(msg: Message, state: FSMContext):
    await state.update_data(datetime=msg.text)
    await msg.answer("Описание работ:")
    await state.set_state(CreateService.work)

@router.message(CreateService.work)
async def work(msg: Message, state: FSMContext):
    await state.update_data(work_description=msg.text)
    await msg.answer("Телефон водителя:")
    await state.set_state(CreateService.phone)

@router.message(CreateService.phone)
async def phone(msg: Message, state: FSMContext):
    data = await state.get_data()
    data["driver_phone"] = msg.text

    service_id = str(uuid.uuid4())
    data["id"] = service_id

    add_pending(data)

    mechanics = get_users_by_role("mechanic")

    text = f"""🚗 Новый сервис

ID: {service_id}
Авто: {data['car_number']}
Дата: {data['datetime']}
Работы: {data['work_description']}
Телефон: {data['driver_phone']}
"""

    for mechanic_id in mechanics:
        try:
            await msg.bot.send_message(
                mechanic_id,
                text,
                reply_markup=confirm_kb(service_id)
            )
        except:
            pass

    await msg.answer("✅ Сервис отправлен механику")
    await state.clear()
