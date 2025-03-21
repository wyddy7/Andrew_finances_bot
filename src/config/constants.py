"""
Константы для бота
"""

# Состояния разговора
(CHOOSING_TYPE, ENTERING_AMOUNT, ENTERING_DESCRIPTION, CHOOSING_CATEGORY) = range(4)

# Регулярные выражения для парсинга транзакций
EXPENSE_PATTERN = r"^-\s*(\d+(?:[.,]\d+)?(?:\s*\d+)*)\s*(?:руб(?:лей|\.)?|р\.)?\s*(.+)$"
INCOME_PATTERN = r"^\+\s*(\d+(?:[.,]\d+)?(?:\s*\d+)*)\s*(?:руб(?:лей|\.)?|р\.)?\s*(.+)$"

# Лимиты
MAX_TRANSACTIONS_PER_10_MIN = 100
TRANSACTION_WINDOW_SECONDS = 600  # 10 минут

# Настройки логирования
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_FILE_BACKUP_COUNT = 5

# Системные сообщения
SYSTEM_ENV_FILE_NOT_FOUND = "Файл .env не найден"
SYSTEM_ENV_FILE_PERMISSIONS = "Небезопасные права доступа к файлу .env: {permissions}"
SYSTEM_ENV_VARS_MISSING = "Отсутствуют необходимые переменные окружения: {vars}"
SYSTEM_TOKEN_NOT_SET = "Токен бота не установлен"
