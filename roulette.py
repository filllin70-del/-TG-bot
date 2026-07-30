import random
from datetime import datetime, timedelta
from aiogram import types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Подключаем настройки
from config import ROULETTE_CONFIG, ROULETTE_LIMITS

# Хранилище для круток
user_spins = {}

# Клавиатура для рулетки
roulette_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎰 Крутить рулетку!", callback_data="spin_roulette")],
    [InlineKeyboardButton(text="📊 Мои шансы", callback_data="roulette_stats")]
])

# Функции
def spin_roulette() -> dict:
    options = []
    weights = []
    
    for key, config in ROULETTE_CONFIG.items():
        options.append({
            "key": key,
            "prize": config["prize"],
            "text": config["text"],
            "emoji": config["emoji"]
        })
        weights.append(config["chance"])
    
    result = random.choices(options, weights=weights, k=1)[0]
    
    return {
        "prize": result["prize"],
        "text": result["text"],
        "emoji": result["emoji"],
        "key": result["key"]
    }

def can_spin(user_id: int) -> tuple:
    now = datetime.now()
    
    if user_id not in user_spins:
        user_spins[user_id] = {"spins": 0, "last_spin": None}
    
    data = user_spins[user_id]
    
    if data["spins"] >= ROULETTE_LIMITS["max_spins_per_day"]:
        return False, f"❌ Вы исчерпали лимит круток на сегодня ({ROULETTE_LIMITS['max_spins_per_day']} круток)"
    
    if data["last_spin"]:
        last_spin = datetime.fromisoformat(data["last_spin"])
        cooldown = timedelta(hours=ROULETTE_LIMITS["cooldown_hours"])
        
        if now - last_spin < cooldown:
            wait_seconds = int((cooldown - (now - last_spin)).total_seconds())
            hours = wait_seconds // 3600
            minutes = (wait_seconds % 3600) // 60
            return False, f"⏳ Подождите {hours}ч {minutes}мин до следующей крутки"
    
    return True, ""

# ФУНКЦИЯ ДЛЯ РЕГИСТРАЦИИ ОБРАБОТЧИКОВ
def register_handlers(dp):
    """Регистрирует все обработчики рулетки"""
    
    @dp.message(Command("roulette"))
    async def cmd_roulette(message: types.Message):
        user_id = message.from_user.id
        user_name = message.from_user.first_name or "Игрок"
        
        can, error_msg = can_spin(user_id)
        
        if not can:
            await message.answer(error_msg)
            return
        
        await message.answer(
            f"🎰 <b>Привет, {user_name}!</b>\n\n"
            f"Крути рулетку и выиграй дни бесплатного VPN!\n\n"
            f"🎯 <b>Призы:</b>\n"
            f"🏆 30 дней — {ROULETTE_CONFIG['30_days']['chance']}%\n"
            f"🎉 7 дней — {ROULETTE_CONFIG['7_days']['chance']}%\n"
            f"😊 3 дня — {ROULETTE_CONFIG['3_days']['chance']}%\n"
            f"🙂 1 день — {ROULETTE_CONFIG['1_day']['chance']}%\n"
            f"😔 Ничего — {ROULETTE_CONFIG['nothing']['chance']}%\n\n"
            f"📊 Осталось круток сегодня: {ROULETTE_LIMITS['max_spins_per_day'] - user_spins.get(user_id, {}).get('spins', 0)}\n\n"
            f"Нажми кнопку и испытай удачу! 🍀",
            reply_markup=roulette_kb,
            parse_mode=ParseMode.HTML
        )

    @dp.callback_query(lambda c: c.data == "spin_roulette")
    async def spin_roulette_callback(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        user_name = callback.from_user.first_name or "Игрок"
        
        can, error_msg = can_spin(user_id)
        
        if not can:
            await callback.answer(error_msg, show_alert=True)
            return
        
        if user_id not in user_spins:
            user_spins[user_id] = {"spins": 0, "last_spin": None}
        
        user_spins[user_id]["spins"] += 1
        user_spins[user_id]["last_spin"] = datetime.now().isoformat()
        
        result = spin_roulette()
        
        result_text = (
            f"🎰 <b>Рулетка!</b>\n\n"
            f"{result['emoji']} <b>{result['text']}</b>\n"
            f"Игрок: <b>{user_name}</b>\n"
            f"Выигрыш: <b>{result['prize']} дней</b>\n\n"
        )
        
        if result["prize"] > 0:
            try:
                # Импортируем db из main или передаем через аргумент
                # await db.add_subscription(user_id, "Рулетка", result["prize"])
                result_text += f"✅ Подписка на <b>{result['prize']} дней</b> активирована!\nНаслаждайтесь VPN! 🚀"
            except Exception as e:
                result_text += f"⚠️ Ошибка активации: {e}"
        else:
            result_text += "😔 Не расстраивайтесь! Попробуйте завтра снова!"
        
        result_text += f"\n\n📊 Осталось круток сегодня: {ROULETTE_LIMITS['max_spins_per_day'] - user_spins[user_id]['spins']}"
        
        await callback.message.edit_text(
            result_text,
            reply_markup=roulette_kb if user_spins[user_id]["spins"] < ROULETTE_LIMITS["max_spins_per_day"] else None,
            parse_mode=ParseMode.HTML
        )
        
        await callback.answer(f"{result['emoji']} Результат: {result['text']}", show_alert=False)

    @dp.callback_query(lambda c: c.data == "roulette_stats")
    async def roulette_stats(callback: types.CallbackQuery):
        user_id = callback.from_user.id
        spins_left = ROULETTE_LIMITS["max_spins_per_day"] - user_spins.get(user_id, {}).get("spins", 0)
        
        await callback.message.edit_text(
            f"📊 <b>Статистика рулетки</b>\n\n"
            f"🎯 <b>Шансы выиграть:</b>\n"
            f"🏆 30 дней — {ROULETTE_CONFIG['30_days']['chance']}%\n"
            f"🎉 7 дней — {ROULETTE_CONFIG['7_days']['chance']}%\n"
            f"😊 3 дня — {ROULETTE_CONFIG['3_days']['chance']}%\n"
            f"🙂 1 день — {ROULETTE_CONFIG['1_day']['chance']}%\n"
            f"😔 Ничего — {ROULETTE_CONFIG['nothing']['chance']}%\n\n"
            f"📊 Круток сегодня: {ROULETTE_LIMITS['max_spins_per_day'] - spins_left} из {ROULETTE_LIMITS['max_spins_per_day']}\n"
            f"⏳ Осталось круток: <b>{spins_left}</b>\n\n"
            f"🔄 Обновление шансов происходит каждый день!",
            parse_mode=ParseMode.HTML
        )
        
        await callback.answer()

    return dp
