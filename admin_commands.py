# admin_commands.py
@dp.message(Command("set_chance"))
async def set_chance(message: types.Message):
    """Только для админов! Изменение шансов"""
    # Проверка на админа
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Доступ запрещен")
        return
    
    # Формат: /set_chance 30_days 15 (изменить шанс 30 дней на 15%)
    args = message.text.split()
    if len(args) != 3:
        await message.answer(
            "Использование: /set_chance <приз> <шанс>\n"
            "Пример: /set_chance 30_days 15\n"
            "Варианты: 30_days, 7_days, 3_days, 1_day, nothing"
        )
        return
    
    prize_key, new_chance = args[1], int(args[2])
    
    if prize_key not in ROULETTE_CONFIG:
        await message.answer("❌ Неверный ключ приза")
        return
    
    # Проверка суммы шансов
    total_chance = new_chance
    for key, config in ROULETTE_CONFIG.items():
        if key != prize_key:
            total_chance += config["chance"]
    
    if total_chance != 100:
        await message.answer(
            f"⚠️ Сумма шансов должна быть 100%!\n"
            f"Сейчас будет: {total_chance}%\n"
            f"Измените другие шансы"
        )
        return
    
    ROULETTE_CONFIG[prize_key]["chance"] = new_chance
    await message.answer(
        f"✅ Шанс для {ROULETTE_CONFIG[prize_key]['text']} изменен на {new_chance}%"
    )
