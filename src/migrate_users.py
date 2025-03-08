"""
Скрипт для упрощения модели User в базе данных.
Удаляет лишние поля из таблицы users (username, first_name, last_name),
сохраняя только id и telegram_id.
"""

from sqlalchemy import text
from src.database import SessionLocal, engine
import sqlite3


def run_user_migration():
    # Используем непосредственно сессию SQLAlchemy
    db = SessionLocal()
    connection = db.connection()

    try:
        # 1. Создаем временную таблицу только с нужными полями
        connection.execute(
            text(
                """
        CREATE TABLE users_new (
            id INTEGER PRIMARY KEY,
            telegram_id BIGINT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
            )
        )

        # 2. Копируем данные из старой таблицы в новую
        connection.execute(
            text(
                """
        INSERT INTO users_new (id, telegram_id, created_at)
        SELECT id, telegram_id, created_at FROM users
        """
            )
        )

        # 3. Удаляем старую таблицу
        connection.execute(text("DROP TABLE users"))

        # 4. Переименовываем новую таблицу
        connection.execute(text("ALTER TABLE users_new RENAME TO users"))

        # Фиксируем изменения
        db.commit()
        print("Миграция модели User успешно выполнена!")

    except Exception as e:
        # В случае ошибки откатываем изменения
        db.rollback()
        print(f"Ошибка при выполнении миграции: {e}")
    finally:
        # Закрываем соединение
        db.close()


if __name__ == "__main__":
    run_user_migration()
