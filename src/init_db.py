import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sqlalchemy import create_engine
from src.models import Base, Category
from src.database import SessionLocal


def init_db():
    # Создаем все таблицы
    db_path = os.path.join("data", "finance_bot.db")
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)

    # Создаем сессию
    db = SessionLocal()

    # Создаем базовые категории
    default_categories = [
        "Продукты",
        "Транспорт",
        "Жилье",
        "Развлечения",
        "Здоровье",
        "Одежда",
        "Образование",
        "Техника",
        "Подарки",
        "Связь",
        "Без категории",
    ]

    # Проверяем существующие категории
    existing_categories = {cat.name.lower() for cat in db.query(Category).all()}

    # Добавляем недостающие категории
    for category_name in default_categories:
        if category_name.lower() not in existing_categories:
            category = Category(name=category_name)
            db.add(category)

    try:
        db.commit()
        print("База данных успешно инициализирована!")
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
