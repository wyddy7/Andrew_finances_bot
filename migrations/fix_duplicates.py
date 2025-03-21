from src.database import SessionLocal
from src.models import Category, Transaction


def remove_duplicates():
    session = SessionLocal()
    try:
        # Получаем все категории "Без категории"
        default_categories = (
            session.query(Category).filter(Category.name == "Без категории").all()
        )

        if len(default_categories) > 1:
            print(f"Найдено {len(default_categories)} категорий 'Без категории'")
            # Оставляем первую категорию
            main_category = default_categories[0]
            print(f"Оставляем категорию с ID: {main_category.id}")

            # Обрабатываем остальные категории
            for category in default_categories[1:]:
                print(f"Обрабатываем дубликат с ID: {category.id}")
                # Переносим все транзакции на основную категорию
                transactions_count = (
                    session.query(Transaction)
                    .filter(Transaction.category_id == category.id)
                    .update({"category_id": main_category.id})
                )
                print(f"Перенесено {transactions_count} транзакций")

                # Удаляем дубликат категории
                session.delete(category)
                print(f"Удален дубликат категории с ID: {category.id}")

            session.commit()
            print("Все дубликаты успешно удалены")
        else:
            print("Дубликатов категории 'Без категории' не найдено")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    remove_duplicates()
