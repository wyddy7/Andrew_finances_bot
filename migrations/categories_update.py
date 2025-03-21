from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from src.models import Base, Category, Transaction
from src.database import DATABASE_URL

# Создаем подключение к базе данных
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def migrate_categories():
    """Миграция категорий: обновление существующих и добавление новых"""
    session = SessionLocal()
    try:
        print("Начинаем миграцию категорий...")

        # Словарь новых категорий и их ключевых слов
        new_categories = {
            "Продукты": [
                "продукты",
                "еда",
                "магазин",
                "супермаркет",
                "пятерочка",
                "магнит",
                "перекресток",
                "ашан",
                "лента",
                "вкусвилл",
                "обед",
                "ужин",
                "завтрак",
                "перекус",
                "кофе",
                "чай",
                "вода",
                "шоколад",
                "фрукты",
                "овощи",
                "хлеб",
                "молоко",
            ],
            "Быт": [
                "квартира",
                "дом",
                "ремонт",
                "мебель",
                "техника",
                "посуда",
                "химия",
                "уборка",
                "жкх",
                "интернет",
                "связь",
                "счета",
                "коммуналка",
                "квартплата",
                "аренда",
                "бытовая",
                "порошок",
                "мыло",
                "шампунь",
                "полотенца",
                "постельное",
            ],
            "Транспорт": [
                "такси",
                "метро",
                "автобус",
                "маршрутка",
                "электричка",
                "каршеринг",
                "самокат",
                "велосипед",
                "проезд",
                "билет",
                "бензин",
                "парковка",
                "яндекс",
                "убер",
                "дорога",
            ],
            "Здоровье": [
                "лекарства",
                "врач",
                "аптека",
                "медицина",
                "больница",
                "анализы",
                "стоматолог",
                "окулист",
                "витамины",
                "массаж",
                "спорт",
                "фитнес",
                "тренировка",
                "бассейн",
                "стрижка",
            ],
            "Одежда": [
                "одежда",
                "обувь",
                "куртка",
                "брюки",
                "рубашка",
                "платье",
                "кроссовки",
                "зара",
                "юникло",
                "спортмастер",
                "остин",
                "носки",
                "белье",
                "шапка",
                "перчатки",
                "сумка",
            ],
            "Развитие": [
                "курсы",
                "обучение",
                "книги",
                "образование",
                "тренинг",
                "семинар",
                "мастер-класс",
                "репетитор",
                "школа",
                "институт",
                "язык",
                "программа",
                "подписка",
                "журнал",
                "вебинар",
            ],
            "Подарки": [
                "подарок",
                "сувенир",
                "праздник",
                "день рождения",
                "новый год",
                "8 марта",
                "23 февраля",
                "цветы",
                "открытка",
                "конфеты",
                "торт",
                "украшение",
                "поздравление",
                "юбилей",
                "свадьба",
            ],
            "Досуг": [
                "кино",
                "театр",
                "концерт",
                "музей",
                "выставка",
                "ресторан",
                "кафе",
                "бар",
                "клуб",
                "боулинг",
                "кальян",
                "игры",
                "развлечения",
                "отдых",
                "хобби",
                "путешествия",
            ],
            "Переводы": [
                "перевод",
                "сбер",
                "тинькофф",
                "альфа",
                "втб",
                "карта",
                "счет",
                "банк",
                "кредит",
                "долг",
                "займ",
                "вернул",
                "отдал",
                "комиссия",
                "проценты",
                "ипотека",
            ],
        }

        # 1. Добавляем новые категории
        for category_name in new_categories.keys():
            category = (
                session.query(Category)
                .filter(func.lower(Category.name) == func.lower(category_name))
                .first()
            )

            if not category:
                print(f"Добавляем новую категорию: {category_name}")
                category = Category(name=category_name)
                session.add(category)

        # Убеждаемся, что у нас есть только одна категория "Без категории"
        default_categories = (
            session.query(Category)
            .filter(func.lower(Category.name) == "без категории")
            .all()
        )

        # Если есть несколько категорий "Без категории", оставляем только одну
        if len(default_categories) > 1:
            # Оставляем первую категорию, остальные удаляем
            for category in default_categories[1:]:
                # Переносим все транзакции на первую категорию
                session.query(Transaction).filter(
                    Transaction.category_id == category.id
                ).update({"category_id": default_categories[0].id})
                # Удаляем дубликат категории
                session.delete(category)
                print(f"Удаляем дубликат категории 'Без категории' (id: {category.id})")

            session.commit()
            default_category = default_categories[0]
        elif len(default_categories) == 1:
            default_category = default_categories[0]
        else:
            print("Добавляем категорию 'Без категории'")
            default_category = Category(name="Без категории")
            session.add(default_category)
            session.commit()

        # 2. Удаляем неиспользуемые категории
        all_categories = session.query(Category).all()
        for category in all_categories:
            # Пропускаем категории, которые есть в новом списке или "Без категории"
            if (
                category.name.lower() in [c.lower() for c in new_categories.keys()]
                or category.name.lower() == "без категории"
            ):
                continue

            # Проверяем, есть ли транзакции с этой категорией
            transactions = (
                session.query(Transaction)
                .filter(Transaction.category_id == category.id)
                .first()
            )

            if not transactions:
                print(f"Удаляем неиспользуемую категорию: {category.name}")
                session.delete(category)

        session.commit()

        # 3. Пересортировка транзакций по новым категориям
        transactions = session.query(Transaction).all()
        for transaction in transactions:
            description = transaction.description.lower()
            category_found = False

            # Проверяем каждую категорию
            for category_name, keywords in new_categories.items():
                if any(keyword.lower() in description for keyword in keywords):
                    category = (
                        session.query(Category)
                        .filter(func.lower(Category.name) == func.lower(category_name))
                        .first()
                    )
                    if category and transaction.category_id != category.id:
                        print(
                            f"Обновляем категорию для транзакции: {transaction.description}"
                        )
                        transaction.category_id = category.id
                        category_found = True
                        break

            # Если категория не найдена, присваиваем "Без категории"
            if not category_found and transaction.category_id != default_category.id:
                transaction.category_id = default_category.id

        session.commit()
        print("Миграция категорий завершена успешно!")

    except Exception as e:
        print(f"Ошибка при миграции категорий: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    migrate_categories()
