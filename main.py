import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from aiogram.client.session.aiohttp import AiohttpSession

# 1. Загружаем токен из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Проверка, чтобы не ломать голову, если токена нет
if not TOKEN:
    print("❌ Ошибка: Токен не найден в файле .env")
    exit()

# 2. Настройка бота
# Мы включаем HTML-разметку по умолчанию, чтобы можно было писать жирным и курсивом
bot = Bot(
    token=TOKEN,
    #token=TOKEN, session=session,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# 3. Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет!\n"
        "Я твой первый бот. Напиши мне что-нибудь, и я повторю."
    )

# 4. Обработчик любого текста (Эхо)
@dp.message()
async def echo_handler(message: types.Message):
    # Бот просто отправляет обратно тот же текст
    await message.answer(message.text)

# 5. Функция запуска
async def main():
    print("🚀 Бот запущен! Нажмите Ctrl+C, чтобы остановить.")
    await dp.start_polling(bot)
    #session: session = AiohttpSession(proxy='184.82.168.146:8080')

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
