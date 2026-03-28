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


# 🔥 ВОТ ГЛАВНЫЙ ФИКС
@router.callback_query(F.data.startswith("cancel:"))
async def cancel(cb: CallbackQuery):
    service_id = cb.data.split(":")[1]

    service = get_by_id(service_id)

    if not service:
        await cb.answer("❌ Сервис не найден", show_alert=True)
        return

    # ❗ НЕЛЬЗЯ отменить если уже принят
    if service.get("status") != "pending":
        await cb.answer("❌ Нельзя отменить — сервис уже принят", show_alert=True)
        return

    delete_pending(service_id)

    await cb.message.answer("❌ Сервис отменён")
    await cb.answer()
