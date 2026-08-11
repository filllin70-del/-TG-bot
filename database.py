import asyncpg
import os
from dotenv import load_dotenv
import traceback  # ← добавляем

load_dotenv()

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        try:
            host = os.getenv("DB_HOST")
            port = os.getenv("DB_PORT", "5432")
            database = os.getenv("DB_NAME")
            user = os.getenv("DB_USER")
            password = os.getenv("DB_PASSWORD")
            
            print(f"🔍 DB_HOST: {host}")
            print(f"🔍 DB_PORT: {port}")
            print(f"🔍 DB_NAME: {database}")
            print(f"🔍 DB_USER: {user}")
            print(f"🔍 DB_PASSWORD: {'SET' if password else 'NOT SET'}")
            
            if not all([host, database, user, password]):
                print("❌ Не все переменные окружения установлены!")
                return False
            
            print(f"🔗 Подключение к БД: {host}:{port}/{database}")
            
            self.pool = await asyncpg.create_pool(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                min_size=1,
                max_size=10,
                timeout=30,
                ssl='require'  # ← ЯВНО УКАЗЫВАЕМ SSL!
            )
            print("✅ Подключение к PostgreSQL установлено!")
            await self.create_tables()
            return True
            
        except Exception as e:
            # Показываем ПОЛНУЮ ошибку
            print(f"❌ ОШИБКА ПОДКЛЮЧЕНИЯ:")
            print(f"   Тип: {type(e).__name__}")
            print(f"   Сообщение: {e}")
            print(f"   Полный traceback:")
            traceback.print_exc()
            return False

    async def create_tables(self):
        """Создает таблицы, если их нет"""
        try:
            async with self.pool.acquire() as conn:
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
        except Exception as e:
            print(f"⚠️ Ошибка при создании таблиц: {e}")

    async def add_user(self, user_id: int, username: str = None, first_name: str = None):
        if self.pool is None:
            print(f"⚠️ БД не подключена! Пользователь {first_name} НЕ сохранен")
            return
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
        if self.pool is None:
            return None
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)

    async def add_subscription(self, user_id: int, tariff: str, days: int):
        if self.pool is None:
            print(f"⚠️ БД не подключена! Подписка {tariff} НЕ сохранена")
            return
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE subscriptions SET is_active = False WHERE user_id = $1
            """, user_id)
            await conn.execute("""
                INSERT INTO subscriptions (user_id, tariff, start_date, end_date, is_active)
                VALUES ($1, $2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + ($3 || ' days')::INTERVAL, True)
            """, user_id, tariff, days)

    async def get_active_subscription(self, user_id: int):
        if self.pool is None:
            return None
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("""
                SELECT * FROM subscriptions 
                WHERE user_id = $1 AND is_active = True AND end_date > CURRENT_TIMESTAMP
            """, user_id)
