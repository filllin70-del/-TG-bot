# комментарии чисто для себя :)
import subprocess
import sys

# Установка aiogram
subprocess.check_call([
    sys.executable, "-m", "pip", "install",
    "aiogram==3.4.1",
    "python-dotenv==1.0.0",
    "aiohttp==3.9.1"
])

# Теперь импортируем библиотеки
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
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

# 1. Главное меню
main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔐 Подключить VPN")],
        [KeyboardButton(text="💳 Оплатить")],
        [KeyboardButton(text="📊 Статус подписки")],
        [KeyboardButton(text="❓ Помощь")]
    ],
    resize_keyboard=True,  # Уменьшить под размер экрана
    one_time_keyboard=False  # Не скрывать после нажатия
)

# 2. Меню выбора 
tariffs_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🌍 Базовый - 1 месяц", callback_data="tariff_base"),
        InlineKeyboardButton(text="🚀 Премиум - 3 месяца", callback_data="tariff_premium")
    ],
    [
        InlineKeyboardButton(text="💎 Безлимит - 12 месяцев", callback_data="tariff_unlimited"),
        InlineKeyboardButton(text="🎁 Промокод", callback_data="promo")
    ],
    [
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
    ]
])

# 3. Клавиатура для оплаты
payment_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="💳 Оплатить картой", callback_data="pay_card"),
        InlineKeyboardButton(text="🪙 Оплатить криптой", callback_data="pay_crypto")
    ],
    [
        InlineKeyboardButton(text="📱 По номеру телефона", callback_data="pay_phone")
    ],
    [
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
    ]
])

# 4. Клавиатура для поддержки
support_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="📝 Написать в поддержку", callback_data="support_write"),
        InlineKeyboardButton(text="❓ Частые вопросы", callback_data="faq")
    ],
    [
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
    ]
])

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    name = message.from_user.first_name or "Гость"
    await message.answer(
        f"👋 Привет, {name} ! Добро пожаловать!"
        "🔒 <b>Ваша приватность — наш приоритет.</b>\n\n"
        "Этот бот предоставляет качественный VPN-доступ в один клик.\n"
        "Мы не храним логи, а наши серверы находятся по всему миру.\n\n"
        "🎯 <b>Чтобы начать:</b>\n"
        "Просто выберите тариф в меню ниже и оплатите подписку.\n"
        "Готовые настройки придут вам сразу после оплаты.\n\n"
        "Приятного серфинга! 🌊",
        reply_markup=main_menu_kb  # Добавляем главное меню
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "❓ <b>Возникли вопросы?</b>\n\n"
        "Обращайтесь в техподдержку.\n"
        "⏱ Время ожидания ответа может занять до нескольких часов.\n"
        "Мы обязательно ответим вам! 🙌",
        reply_markup=support_kb
    )

@dp.message(Command("VPN"))
async def cmd_VPN(message: types.Message):
    await message.answer(
        "🌍 <b>Подключить VPN_GAZ</b>\n\n"
        "Выберите подходящий тариф:",
        reply_markup=tariffs_kb
    )

@dp.message(Command("PAY"))
async def cmd_PAY(message: types.Message):
    await message.answer(
        "💳 <b>Оплатить VPN</b>\n\n"
        "Выберите удобный способ оплаты:",
        reply_markup=payment_kb
    )

@dp.message(Command("podpiska"))
async def cmd_podpiska(message: types.Message):
    # Пример ответа с информацией о подписке
    await message.answer(
        "📊 <b>Статус подписки</b>\n\n"
        "✅ У вас активна подписка: <bНеактивна></b>\n"
        "📅 Действует до: <b>Неактивна</b>\n"
        "📈 Осталось дней: <b>0</b>\n\n"
        "Хотите продлить или сменить тариф?",
        reply_markup=tariffs_kb
    )

# Обработка текстовых кнопок
@dp.message(lambda message: message.text == "🔐 Подключить VPN")
async def vpn_button(message: types.Message):
    await cmd_VPN(message)

@dp.message(lambda message: message.text == "💳 Оплатить")
async def pay_button(message: types.Message):
    await cmd_PAY(message)

@dp.message(lambda message: message.text == "📊 Статус подписки")
async def subscription_button(message: types.Message):
    await cmd_podpiska(message)

@dp.message(lambda message: message.text == "❓ Помощь")
async def help_button(message: types.Message):
    await cmd_help(message)

@dp.callback_query(lambda c: c.data == "tariff_base")
async def tariff_base(callback: types.CallbackQuery):
    await callback.answer("✅ Выбран тариф Базовый")
    await callback.message.edit_text(
        "🌍 <b>Тариф Базовый</b>\n\n"
        "💰 Цена: <b>--- ₽/мес</b>\n"
        "📊 Скорость: до <b>50 Мбит/с</b>\n"
        "🌐 Серверов: <b>5</b>\n"
        "📱 Устройств: <b>2</b>\n\n"
        "Для оплаты нажмите кнопку ниже:",
        reply_markup=payment_kb
    )

@dp.callback_query(lambda c: c.data == "tariff_premium")
async def tariff_premium(callback: types.CallbackQuery):
    await callback.answer("✅ Выбран тариф Премиум")
    await callback.message.edit_text(
        "🚀 <b>Тариф Премиум</b>\n\n"
        "💰 Цена: <b>--- ₽/3 мес</b>\n"
        "📊 Скорость: до <b>200 Мбит/с</b>\n"
        "🌐 Серверов: <b>15</b>\n"
        "📱 Устройств: <b>5</b>\n\n"
        "Для оплаты нажмите кнопку ниже:",
        reply_markup=payment_kb
    )

@dp.callback_query(lambda c: c.data == "tariff_unlimited")
async def tariff_unlimited(callback: types.CallbackQuery):
    await callback.answer("✅ Выбран тариф Безлимит")
    await callback.message.edit_text(
        "💎 <b>Тариф Безлимит</b>\n\n"
        "💰 Цена: <b>--- ₽/год</b>\n"
        "📊 Скорость: до <b>500 Мбит/с</b>\n"
        "🌐 Серверов: <b>30+</b>\n"
        "📱 Устройств: <b>10</b>\n"
        "🎁 <b>Безлимитный трафик!</b>\n\n"
        "Для оплаты нажмите кнопку ниже:",
        reply_markup=payment_kb
    )

@dp.callback_query(lambda c: c.data == "promo")
async def promo(callback: types.CallbackQuery):
    await callback.answer("Введите промокод")
    await callback.message.edit_text(
        "🎁 <b>Введите промокод</b>\n\n"
        "Если у вас есть промокод, отправьте его сообщением.\n"
        "Пример: <code>VPN2026</code>"
    )

@dp.callback_query(lambda c: c.data == "pay_card")
async def pay_card(callback: types.CallbackQuery):
    await callback.answer("💳 Оплата картой")
    await callback.message.edit_text(
        "💳 <b>Оплата банковской картой</b>\n\n"
        "Для оплаты перейдите по ссылке:\n"
        "🔗 <a href='скоро тут будет ссылка'>Оплатить сейчас</a>\n\n"
        "После оплаты настройки придут автоматически."
    )

@dp.callback_query(lambda c: c.data == "pay_crypto")
async def pay_crypto(callback: types.CallbackQuery):
    await callback.answer("🪙 Оплата криптовалютой")
    await callback.message.edit_text(
        "🪙 <b>Оплата криптовалютой</b>\n\n"
        "Мы принимаем:\n"
        "• BTC (Bitcoin)\n"
        "• ETH (Ethereum)\n"
        "• USDT (TRC20)\n\n"
        "Для получения реквизитов нажмите:\n"
        "🔗 <a href='скоро тут что-то будет'>Получить реквизиты</a>"
    )

@dp.callback_query(lambda c: c.data == "pay_phone")
async def pay_phone(callback: types.CallbackQuery):
    await callback.answer("📱 Оплата по номеру телефона")
    await callback.message.edit_text(
        "📱 <b>Оплата по номеру телефона</b>\n\n"
        "Отправьте ваш номер в формате:\n"
        "<code>+7 999 123 4567</code>\n\n"
        "Мы пришлем ссылку для оплаты."
    )

@dp.callback_query(lambda c: c.data == "support_write")
async def support_write(callback: types.CallbackQuery):
    await callback.answer("📝 Связь с поддержкой")
    await callback.message.edit_text(
        "📝 <b>Техническая поддержка</b>\n\n"
        "Опишите вашу проблему одним сообщением.\n"
        "Мы ответим в ближайшее время (до нескольких часов).\n\n"
        "⏱ <i>Среднее время ответа: 7 дней и 8 ночей (шутка, ответим сразу)</i>"
    )

@dp.callback_query(lambda c: c.data == "faq")
async def faq(callback: types.CallbackQuery):
    await callback.answer("❓ Частые вопросы")
    await callback.message.edit_text(
        "❓ <b>Частые вопросы</b>\n\n"
        "<b>1. Как подключить VPN?</b>\n"
        "Выберите тариф и оплатите подписку.\n\n"
        "<b>2. Сколько серверов?</b>\n"
        "От 5 до 30+ в зависимости от тарифа.\n\n"
        "<b>3. Есть ли пробный период?</b>\n"
        "Да, 3 дня бесплатно при регистрации.\n\n"
        "<b>4. Как отменить подписку?</b>\n"
        "Напишите в поддержку.\n\n"
        "Для связи с поддержкой нажмите кнопку назад."
    )

@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.answer("↩️ Возврат в главное меню")
    await callback.message.edit_text(
        "🔒 <b>Главное меню</b>\n\n"
        "Выберите действие:",
        reply_markup=main_menu_kb
    )

@dp.message()
async def echo_handler(message: types.Message):
    # Обработка всех остальных сообщений (включая промокоды)
    await message.answer(
        "Я вас не понял. Используйте кнопки меню или команды:\n"
        "/start - Главное меню\n"
        "/help - Помощь\n"
        "/VPN - Выбрать тариф\n"
        "/PAY - Оплата\n"
        "/podpiska - Статус подписки"
    )

async def main():
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
