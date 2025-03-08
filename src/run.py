#!/usr/bin/env python3
import sys
import os

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bot import FinanceBot
from src.logger import bot_logger


def main():
    try:
        # Создаем и запускаем бота
        bot = FinanceBot()
        bot.run()
    except KeyboardInterrupt:
        bot_logger.info("Бот остановлен пользователем")
    except Exception as e:
        bot_logger.error(f"Критическая ошибка: {e}", exc_info=True)


if __name__ == "__main__":
    main()
