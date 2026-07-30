# config.py - настройки рулетки
ROULETTE_CONFIG = {
    "30_days": {
        "chance": 1,      # 1% шанс выиграть 30 дней
        "prize": 30,
        "emoji": "🏆",
        "text": "ДЖЕКПОТ! 30 дней!"
    },
    "7_days": {
        "chance": 4,      # 4% шанс выиграть 7 дней
        "prize": 7,
        "emoji": "🎉",
        "text": "Отлично! 7 дней!"
    },
    "3_days": {
        "chance": 10,     # 10% шанс выиграть 3 дня
        "prize": 3,
        "emoji": "😊",
        "text": "Неплохо! 3 дня!"
    },
    "1_day": {
        "chance": 20,     # 20% шанс выиграть 1 день
        "prize": 1,
        "emoji": "🙂",
        "text": "Бесплатный день!"
    },
    "nothing": {
        "chance": 65,     # 65% шанс ничего не выиграть
        "prize": 0,
        "emoji": "😔",
        "text": "Попробуй ещё раз!"
    }
}

# Ограничения
ROULETTE_LIMITS = {
    "max_spins_per_day": 3,  # Максимум круток в день
    "cooldown_hours": 2      # Ожидание между крутками (часы)
}
