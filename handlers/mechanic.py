from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from sheets.completed import add_completed
from sheets.pending import get_pending, delete_pending, get_by_id
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
    await state.update_data(datetime=msg.text)
    await msg.answer("NETTO:")
    await state.set_state(AddService.netto)

@router.message(AddService.netto)
async def netto(msg: Message, state: FSMContext):
    netto = normalize_money(msg.text)
    await state.update_data(netto=netto)
    await msg.answer("Комментарий:")
    await state.set_state(AddService.comment)

@router.message(AddService.comment)
async def comment(msg: Message, state: FSMContext):
    data = await state.get_data()
    data["comment"] = msg.text

    user_display = get_user_display(msg.from_user)

    data["created_by"] = user_display
    data["completed_by"] = user_display

    add_completed(data)

    await msg.answer("✅ Сервис добавлен вручную")
    await state.clear()

@router.callback_query(F.data.startswith("finish:"))
async def finish_start(cb: CallbackQuery, state: FSMContext):
    await state.update_data(service_id=cb.data.split(":")[1])
    await cb.message.answer("NETTO:")
    await state.set_state(FinishService.netto)

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
        "comment": msg.text,
        "created_by": service.get("created_by", ""),
        "completed_by": get_user_display(msg.from_user)
    }

    add_completed(result)
    delete_pending(data["service_id"])

    await msg.answer("✅ Сервис завершён")
    await state.clear()
