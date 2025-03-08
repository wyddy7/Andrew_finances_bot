from sqlalchemy import create_engine
from models import Base, Category
from database import SessionLocal


def init_db():
    # Создаем все таблицы
    engine = create_engine("sqlite:///finance.db")
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
    existing_categories = {cat.name for cat in db.query(Category).all()}

    # Добавляем недостающие категории
    for category_name in default_categories:
        if category_name not in existing_categories:
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
