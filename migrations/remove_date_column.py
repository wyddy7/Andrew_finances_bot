from sqlalchemy import create_engine, text
from src.database import Base, engine, SessionLocal
from src.models import Transaction


def migrate_remove_date():
    """Удаление колонки date из таблицы transactions"""
    try:
        # Создаем подключение к базе данных
        session = SessionLocal()

        # Удаляем колонку date
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE transactions DROP COLUMN date"))
            conn.commit()

        print("Колонка date успешно удалена из таблицы transactions")

    except Exception as e:
        print(f"Ошибка при удалении колонки date: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    migrate_remove_date()
