import subprocess
import sys

# Устанавливаем aiogram прямо здесь
subprocess.check_call([
    sys.executable, "-m", "pip", "install",
    "aiogram==3.4.1",
    "python-dotenv==1.0.0",
    "aiohttp==3.9.1"
])

# Теперь импортируем
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("❌ Ошибка: Токен не найден")
    exit()

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("👋 Привет! Бот работает!")

@dp.message()
async def echo_handler(message: types.Message):
    await message.answer(message.text)

async def main():
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
