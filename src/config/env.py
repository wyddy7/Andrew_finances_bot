"""
Модуль для работы с переменными окружения
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from .constants import (
    SYSTEM_ENV_FILE_NOT_FOUND,
    SYSTEM_ENV_FILE_PERMISSIONS,
    SYSTEM_ENV_VARS_MISSING,
)


def load_environment():
    """
    Загружает и проверяет переменные окружения

    Returns:
        dict: Словарь с загруженными переменными окружения

    Raises:
        FileNotFoundError: Если файл .env не найден
        PermissionError: Если права доступа к файлу .env небезопасны
        EnvironmentError: Если отсутствуют необходимые переменные окружения
    """
    # Проверяем наличие .env файла
    env_file = Path(".env")
    if not env_file.exists():
        raise FileNotFoundError(SYSTEM_ENV_FILE_NOT_FOUND)

    # Проверяем права доступа к .env файлу
    if os.name != "nt":  # Пропускаем проверку для Windows
        env_permissions = oct(os.stat(env_file).st_mode)[-3:]
        if env_permissions != "600":
            raise PermissionError(
                SYSTEM_ENV_FILE_PERMISSIONS.format(permissions=env_permissions)
            )

    # Загружаем переменные окружения
    load_dotenv()

    # Проверяем наличие необходимых переменных окружения
    required_env_vars = ["TELEGRAM_BOT_TOKEN"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        raise EnvironmentError(
            SYSTEM_ENV_VARS_MISSING.format(vars=", ".join(missing_vars))
        )

    # Возвращаем словарь с переменными окружения
    return {
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
        "ADMIN_USER_IDS": [
            int(id) for id in os.getenv("ADMIN_USER_IDS", "").split(",") if id
        ],
    }
