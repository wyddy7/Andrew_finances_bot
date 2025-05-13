import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.models import Base, Category
from src.database import DATABASE_URL

def init_db():
    # Создаем engine заново для инициализации
    engine = create_engine(DATABASE_URL)
    
    # Создаем все таблицы
    Base.metadata.drop_all(bind=engine)  # Сначала удаляем все таблицы
    Base.metadata.create_all(bind=engine)
    
    # Создаем сессию
    session = Session(engine)
    
    try:
        # Создаем базовые категории
        default_categories = [
            "Продукты", "Транспорт", "Жилье", "Развлечения",
            "Здоровье", "Одежда", "Образование", "Техника",
            "Подарки", "Связь", "Без категории"
        ]
        
        # Добавляем категории
        for category_name in default_categories:
            category = Category(name=category_name)
            session.add(category)
        
        session.commit()
        print("База данных успешно инициализирована!")
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    init_db()
