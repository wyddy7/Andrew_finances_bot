from src.database import engine, SessionLocal
from src.models import Base, Category
from sqlalchemy import text


def recreate_categories():
    session = SessionLocal()
    try:
        # Получаем текущие категории
        current_categories = session.query(Category.name).all()
        current_categories = [c[0] for c in current_categories]

        # Пересоздаем таблицу
        Base.metadata.drop_all(bind=engine, tables=[Category.__table__])
        Base.metadata.create_all(bind=engine, tables=[Category.__table__])

        # Определяем порядок категорий
        category_order = [
            "Продукты",
            "Быт",
            "Транспорт",
            "Здоровье",
            "Одежда",
            "Развитие",
            "Подарки",
            "Досуг",
            "Переводы",
            "Без категории",
        ]

        # Добавляем категории в нужном порядке
        for i, name in enumerate(category_order, 1):
            if name in current_categories:
                category = Category(name=name, order=i)
                session.add(category)
                print(f"Добавлена категория: {name} (порядок: {i})")

        session.commit()
        print("Категории успешно обновлены")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    recreate_categories()
