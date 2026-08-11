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

# библиотеки
import asyncio
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
from database import Database

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

db = Database()

# ============ КЛАВИАТУРЫ ============

main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔐 Подключить VPN")],
        [KeyboardButton(text="💳 Оплатить")],
        [KeyboardButton(text="📊 Статус подписки")],
        [KeyboardButton(text="❓ Помощь")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

tariffs_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🌍 1 месяц", callback_data="tariff_base"),
        InlineKeyboardButton(text="🚀 3 месяца", callback_data="tariff_premium")
    ],
    [
        InlineKeyboardButton(text="💎 12 месяцев", callback_data="tariff_unlimited"),
        InlineKeyboardButton(text="🎁 Промокод", callback_data="promo")
    ],
    [
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
    ]
])

payment_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="💳 Оплатить картой", callback_data="pay_card"),
    ],
    [
        InlineKeyboardButton(text="📱 Переводом", callback_data="pay_phone")
    ],
    [
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
    ]
])

support_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="📝 Написать в поддержку", callback_data="support_write"),
        InlineKeyboardButton(text="❓ Частые вопросы", callback_data="faq")
    ],
    [
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
    ]
])


# ============ ОБРАБОТЧИКИ КОМАНД ============

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user = message.from_user
    user_id = user.id
    username = user.username
    first_name = user.first_name
    
    await db.add_user(user_id, username, first_name)
    subscription = await db.get_active_subscription(user_id)
    
    name = first_name or "Гость"
    
    if subscription:
        tariff = subscription['tariff']
        end_date = subscription['end_date'].strftime('%d.%m.%Y')
        status_text = f"✅ У вас активна подписка <b>{tariff}</b> до {end_date}"
    else:
        status_text = "❌ У вас нет активной подписки"
    
    await message.answer(
        f"👋 Привет, {name}!\n\n"
        f"{status_text}\n\n"
        "🔒 <b>Ваша приватность - наш приоритет.</b>\n\n"
        "Этот бот предоставляет качественный VPN-доступ в один клик.\n"
        "Мы не храним логи, а наши серверы находятся по всему миру.\n\n"
        "🎯 <b>Чтобы начать:</b>\n"
        "Просто выберите тариф в меню ниже и оплатите подписку.\n"
        "Готовые настройки придут вам сразу после оплаты.\n\n"
        "Приятного серфинга! 🌊",
        reply_markup=main_menu_kb,
        parse_mode=ParseMode.HTML
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "❓ <b>Возникли вопросы?</b>\n\n"
        "Обращайтесь в техподдержку.\n"
        "⏱ Время ожидания ответа может занять до нескольких часов.\n"
        "Мы обязательно ответим вам! 🙌",
        reply_markup=support_kb,
        parse_mode=ParseMode.HTML
    )


@dp.message(Command("VPN"))
async def cmd_VPN(message: types.Message):
    await message.answer(
        "🌍 <b>Подключить VPN_GAZ</b>\n\n"
        "Выберите подходящий тариф:",
        reply_markup=tariffs_kb,
        parse_mode=ParseMode.HTML
    )


@dp.message(Command("PAY"))
async def cmd_PAY(message: types.Message):
    await message.answer(
        "💳 <b>Оплатить VPN</b>\n\n"
        "Выберите удобный способ оплаты:",
        reply_markup=payment_kb,
        parse_mode=ParseMode.HTML
    )


@dp.message(Command("podpiska"))
async def cmd_podpiska(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Пользователь"
    
    subscription = await db.get_active_subscription(user_id)
    
    if subscription:
        tariff = subscription['tariff']
        end_date = subscription['end_date']
        start_date = subscription['start_date']
        
        end_date_str = end_date.strftime('%d.%m.%Y')
        start_date_str = start_date.strftime('%d.%m.%Y')
        
        days_left = (end_date - datetime.now()).days
        days_left = max(0, days_left)
        
        await message.answer(
            f"📊 <b>Статус подписки</b>\n\n"
            f"👤 Пользователь: <b>{user_name}</b>\n"
            f"✅ Тариф: <b>{tariff}</b>\n"
            f"📅 Активирована: <b>{start_date_str}</b>\n"
            f"📅 Действует до: <b>{end_date_str}</b>\n"
            f"📈 Осталось дней: <b>{days_left}</b>\n\n"
            f"🔄 Статус: <b>🟢 Активна</b>\n\n"
            f"Хотите продлить или сменить тариф?",
            reply_markup=tariffs_kb,
            parse_mode=ParseMode.HTML
        )
    else:
        await message.answer(
            f"📊 <b>Статус подписки</b>\n\n"
            f"👤 Пользователь: <b>{user_name}</b>\n"
            f"❌ У вас <b>нет</b> активной подписки\n\n"
            f"🔄 Статус: <b>🔴 Неактивна</b>\n\n"
            f"Выберите тариф для подключения:",
            reply_markup=tariffs_kb,
            parse_mode=ParseMode.HTML
        )


# ============ ОБРАБОТЧИКИ КНОПОК (Reply) ============

@dp.message(lambda message: message.text == "🔐 Подключить VPN")
async def vpn_button(message: types.Message):
    user = message.from_user
    await db.add_user(user.id, user.username, user.first_name)
    await cmd_VPN(message)


@dp.message(lambda message: message.text == "💳 Оплатить")
async def pay_button(message: types.Message):
    user = message.from_user
    await db.add_user(user.id, user.username, user.first_name)
    await cmd_PAY(message)


@dp.message(lambda message: message.text == "📊 Статус подписки")
async def subscription_button(message: types.Message):
    user = message.from_user
    await db.add_user(user.id, user.username, user.first_name)
    await cmd_podpiska(message)


@dp.message(lambda message: message.text == "❓ Помощь")
async def help_button(message: types.Message):
    user = message.from_user
    await db.add_user(user.id, user.username, user.first_name)
    await cmd_help(message)


# ============ ОБРАБОТЧИКИ INLINE-КНОПОК ============

@dp.callback_query(lambda c: c.data == "tariff_base")
async def tariff_base(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await db.add_subscription(user_id, "Базовый - 1 месяц", 30)
    
    await callback.answer("✅ Выбран тариф Базовый")
    await callback.message.edit_text(
        "🌍 <b>Тариф Базовый</b>\n\n"
        "💰 Цена: <b>159 руб. 1 месяц</b>\n"
        "🌐 Серверов: <b>15+</b>\n"
        "📱 Устройств: <b>2</b>\n\n"
        "Для оплаты нажмите кнопку ниже:",
        reply_markup=payment_kb,
        parse_mode=ParseMode.HTML
    )


@dp.callback_query(lambda c: c.data == "tariff_premium")
async def tariff_premium(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await db.add_subscription(user_id, "Стандарт - 3 месяца", 90)
    
    await callback.answer("✅ Выбран тариф Стандарт")
    await callback.message.edit_text(
        "🚀 <b>Тариф Стандарт</b>\n\n"
        "💰 Цена: <b>359 руб. 3 месяца</b>\n"
        "🌐 Серверов: <b>25+</b>\n"
        "📱 Устройств: <b>5</b>\n\n"
        "Для оплаты нажмите кнопку ниже:",
        reply_markup=payment_kb,
        parse_mode=ParseMode.HTML
    )


@dp.callback_query(lambda c: c.data == "tariff_unlimited")
async def tariff_unlimited(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await db.add_subscription(user_id, "Премиум - 12 месяцев", 365)
    
    await callback.answer("✅ Выбран тариф Премиум")
    await callback.message.edit_text(
        "💎 <b>Тариф Премиум</b>\n\n"
        "💰 Цена: <b>1200 ₽уб. 12 месяцев.</b>\n"
        "🌐 Серверов: <b>50+</b>\n"
        "📱 Устройств: <b>10</b>\n"
        "🎁 <b>Безлимитный трафик!</b>\n\n"
        "Для оплаты нажмите кнопку ниже:",
        reply_markup=payment_kb,
        parse_mode=ParseMode.HTML
    )


@dp.callback_query(lambda c: c.data == "promo")
async def promo(callback: types.CallbackQuery):
    await callback.answer("Введите промокод")
    await callback.message.edit_text(
        "🎁 <b>Введите промокод</b>\n\n"
        "Если у вас есть промокод, отправьте его сообщением.\n"
        "Пример: <code>VPN2026</code>",
        parse_mode=ParseMode.HTML
    )


@dp.callback_query(lambda c: c.data == "pay_card")
async def pay_card(callback: types.CallbackQuery):
    await callback.answer("💳 Оплата картой")
    await callback.message.edit_text(
        "💳 <b>Оплата банковской картой</b>\n\n"
        "Для оплаты перейдите по ссылке:\n"
        "🔗 <a href='http://robokassa/'>Оплатить</a>\n\n"
        "После оплаты настройки придут автоматически.",
        parse_mode=ParseMode.HTML
    )


@dp.callback_query(lambda c: c.data == "pay_phone")
async def pay_phone(callback: types.CallbackQuery):
    await callback.answer("📱 Оплата переводом")
    await callback.message.edit_text(
        "📱 <b>Оплата переводом</b>\n\n"
        "Оплата через банковский перевод:\n"
        "<code>2204311072527493</code>\n\n"
        "Настройки придут в течение 10 минут после оплаты!",
        parse_mode=ParseMode.HTML
    )


@dp.callback_query(lambda c: c.data == "support_write")
async def support_write(callback: types.CallbackQuery):
    await callback.answer("📝 Связь с поддержкой")
    await callback.message.edit_text(
        "📝 <b>Техническая поддержка</b>\n\n"
        "Напишите нам в личные сообщения:\n"
        "Мы ответим в ближайшее время.\n\n"
        "⏱ <i>@bufiteer</i>",
        parse_mode=ParseMode.HTML
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
        "Для связи с поддержкой нажмите кнопку назад.",
        parse_mode=ParseMode.HTML
    )


@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.answer("↩️ Возврат в главное меню")
    await callback.message.delete()
    await callback.message.answer(
        "🔒 <b>Главное меню</b>\n\n"
        "Выберите действие:",
        reply_markup=main_menu_kb,
        parse_mode=ParseMode.HTML
    )


@dp.message()
async def echo_handler(message: types.Message):
    await message.answer(
        "Я вас не понял. Используйте кнопки меню или команды:\n"
        "/start - Главное меню\n"
        "/help - Помощь\n"
        "/VPN - Выбрать тариф\n"
        "/PAY - Оплата\n"
        "/podpiska - Статус подписки"
    )

# ============ ЗАПУСК ============

async def main():
    print("🔄 Проверка подключения к БД...")
    connected = await db.connect()
    
    if connected:
        print("✅ Подключение к PostgreSQL установлено!")
        print("🚀 Бот запущен с подключением к БД!")
    else:
        print("❌ Ошибка подключения к БД!")
        print("⚠️ Бот запущен БЕЗ подключения к БД! Проверьте .env файл.")
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


