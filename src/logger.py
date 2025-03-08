import logging
import logging.handlers
import os
from pathlib import Path


def setup_logger(name: str = "bot_logger") -> logging.Logger:
    """
    Настройка логгера с ротацией файлов и форматированием
    """
    # Создаем директорию для логов если её нет
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Создаем логгер
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Форматтер для логов
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Хендлер для файла с ротацией (максимум 5 файлов по 10MB)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / f"{name}.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Хендлер для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # Добавляем хендлеры к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Создаем логгеры
bot_logger = setup_logger("bot")
metrics_logger = setup_logger("metrics")

__all__ = ["bot_logger", "metrics_logger"]
