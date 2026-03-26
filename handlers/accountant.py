from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from sheets.completed import get_completed_since

router = Router()

class ReportState(StatesGroup):
    date_from = State()

def format_money(value):
    try:
        value = float(value)

        # 🔥 если вдруг 3075 вместо 307.5 → исправляем
        if value > 1000:
            value = value / 10

        return f"{str(round(value,2)).replace('.', ',')} zł"
    except:
        return f"{value} zł"

@router.message(lambda msg: msg.text == "📊 Сделанные сервисы")
async def ask_date(msg: Message, state: FSMContext):
    await msg.answer("Введите дату С (формат: DD.MM.YYYY)")
    await state.set_state(ReportState.date_from)

@router.message(ReportState.date_from)
async def show_report(msg: Message, state: FSMContext):
    date_from = msg.text

    try:
        data = get_completed_since(date_from)
    except:
        await msg.answer("❌ Неверный формат даты")
        return

    if not data:
        await msg.answer("Нет данных за этот период")
        await state.clear()
        return

    text = "📊 Отчёт:\n\n"

    for r in data:
        netto = format_money(r['netto'])
        brutto = format_money(r['brutto'])

        text += f"""🚗 {r['car_number']}
🕒 {r['datetime']}
💰 NETTO: {netto}
💵 BRUTTO: {brutto}
📝 {r['comment']}

"""

    await msg.answer(text)
    await state.clear()
