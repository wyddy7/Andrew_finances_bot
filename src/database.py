from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

# Создаем директорию для базы данных
db_dir = Path("data")
db_dir.mkdir(exist_ok=True)

# Создаем URL подключения к базе данных SQLite
DATABASE_URL = f"sqlite:///{db_dir}/finance_bot.db"

# Создаем движок SQLAlchemy
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базовый класс для моделей
Base = declarative_base()


def get_db():
    """
    Генератор для получения сессии базы данных
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
