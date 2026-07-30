import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        """Создает пул соединений с PostgreSQL"""
        try:
            self.pool = await asyncpg.create_pool(
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT", "5432"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                min_size=1,
                max_size=10,
                timeout=30
            )
            print("✅ Подключение к PostgreSQL установлено!")
            
            # Создаем таблицы
            await self.create_tables()
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            return False

    async def create_tables(self):
        """Создает таблицы, если их нет"""
        async with self.pool.acquire() as conn:
            # Таблица пользователей
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT UNIQUE NOT NULL,
                    username VARCHAR(255),
                    first_name VARCHAR(255),
                    phone VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP
                )
            """)
            
            # Таблица подписок
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(user_id),
                    tariff VARCHAR(50),
                    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_date TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    payment_id VARCHAR(255)
                )
            """)
            
            # Таблица для промокодов
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS promo_codes (
                    id SERIAL PRIMARY KEY,
                    code VARCHAR(50) UNIQUE NOT NULL,
                    discount INTEGER,
                    used_by BIGINT,
                    used_at TIMESTAMP,
                    is_used BOOLEAN DEFAULT FALSE
                )
            """)
            
            print("✅ Таблицы созданы (или уже существуют)")

    # ============ МЕТОДЫ ДЛЯ РАБОТЫ С БАЗОЙ ============
    
    async def add_user(self, user_id: int, username: str = None, first_name: str = None):
        """Добавляет пользователя в БД"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users (user_id, username, first_name, last_active)
                VALUES ($1, $2, $3, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id) DO UPDATE SET
                    username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name,
                    last_active = CURRENT_TIMESTAMP
            """, user_id, username, first_name)

    async def get_user(self, user_id: int):
        """Получает данные пользователя"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                "SELECT * FROM users WHERE user_id = $1",
                user_id
            )

    async def add_subscription(self, user_id: int, tariff: str, days: int):
        """Добавляет подписку пользователю"""
        async with self.pool.acquire() as conn:
            # Деактивируем старые подписки
            await conn.execute("""
                UPDATE subscriptions SET is_active = False
                WHERE user_id = $1
            """, user_id)
            
            # Создаем новую
            await conn.execute("""
                INSERT INTO subscriptions (user_id, tariff, start_date, end_date, is_active)
                VALUES ($1, $2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + ($3 || ' days')::INTERVAL, True)
            """, user_id, tariff, days)

    async def get_active_subscription(self, user_id: int):
        """Проверяет активную подписку"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("""
                SELECT * FROM subscriptions 
                WHERE user_id = $1 AND is_active = True AND end_date > CURRENT_TIMESTAMP
            """, user_id)
