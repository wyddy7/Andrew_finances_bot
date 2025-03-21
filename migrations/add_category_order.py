from src.database import SessionLocal, engine
from src.models import Category, Base
from sqlalchemy import text


def add_order_field():
    session = SessionLocal()
    try:
        # Получаем все существующие категории
        categories = session.query(Category).all()
        category_data = [(c.id, c.name) for c in categories]

        # Удаляем старую таблицу
        with engine.connect() as connection:
            connection.execute(text("DROP TABLE categories"))
            connection.execute(
                text(
                    """
                CREATE TABLE categories (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR NOT NULL UNIQUE,
                    "order" INTEGER DEFAULT 999
                )
            """
                )
            )

        # Задаем порядок категорий
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

        # Восстанавливаем категории с новым порядком
        for cat_id, cat_name in category_data:
            try:
                order = (
                    category_order.index(cat_name) + 1
                    if cat_name in category_order
                    else 999
                )
                with engine.connect() as connection:
                    connection.execute(
                        text(
                            'INSERT INTO categories (id, name, "order") VALUES (:id, :name, :order)'
                        ),
                        {"id": cat_id, "name": cat_name, "order": order},
                    )
            except Exception as e:
                print(f"Ошибка при добавлении категории {cat_name}: {e}")

        print("Порядок категорий успешно обновлен")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    add_order_field()
