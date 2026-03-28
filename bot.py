import asyncio
import logging

from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import start, admin, mechanic, accountant

logging.basicConfig(level=logging.INFO)

async def main():
    print("BOT STARTED 🚀")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(mechanic.router)
    dp.include_router(accountant.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
