from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from sheets.completed import get_completed_since
from services.validation import validate_date

router = Router()


class ReportState(StatesGroup):
    date_from = State()


def format_money(value):
    try:
        value = float(str(value).replace(",", "."))
        return f"{str(round(value, 2)).replace('.', ',')} zł"
    except Exception:
        return f"{value} zł"


@router.message(lambda msg: msg.text == "📊 Сделанные сервисы")
async def ask_date(msg: Message, state: FSMContext):
    await msg.answer("Введите дату С (формат: DD.MM.YYYY)")
    await state.set_state(ReportState.date_from)


@router.message(ReportState.date_from)
async def show_report(msg: Message, state: FSMContext):
    date_from = (msg.text or "").strip()

    if not validate_date(date_from):
        await msg.answer("❌ Неверный формат даты. Пример: 30.03.2026")
        return

    try:
        data = get_completed_since(date_from)
    except Exception:
        await msg.answer("❌ Ошибка при получении данных")
        await state.clear()
        return

    if not data:
        await msg.answer("Нет данных за этот период")
        await state.clear()
        return

    text = "📊 Отчёт:\n\n"

    for r in data:
        netto = format_money(r.get("netto", ""))
        brutto = format_money(r.get("brutto", ""))
        created_by = r.get("created_by", "")
        completed_by = r.get("completed_by", "")

        text += (
            f"🚗 {r.get('car_number', '-')}\n"
            f"🕒 {r.get('datetime', '-')}\n"
            f"💰 NETTO: {netto}\n"
            f"💵 BRUTTO: {brutto}\n"
            f"📝 {r.get('comment', '-')}\n"
        )

        if created_by:
            text += f"👤 Создал: {created_by}\n"
        if completed_by:
            text += f"🔧 Завершил: {completed_by}\n"

        text += "\n"

    await msg.answer(text)
    await state.clear()
