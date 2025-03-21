"""
Модуль содержит все текстовые сообщения бота
"""

# Сообщения для команды /start
START_MESSAGE = (
    "👋 Привет! Я бот для учета финансов.\n\n"
    "🔍 Как меня использовать:\n"
    "1. Добавить расход: -500 за продукты\n"
    "2. Добавить доход: +5000 зарплата\n\n"
    "📋 Основные команды:\n"
    "/balance - текущий баланс 💰\n"
    "/history - история операций 📅\n"
    "/stats - статистика расходов и доходов 📊\n"
    "/category - статистика по категориям 📂\n"
    "/export - выгрузка в Excel 📥\n"
    "/help - подробная справка\n\n"
    "Бот автоматически определяет категории по ключевым словам.\n"
    "💡 Используйте /help для просмотра всех категорий и подробной инструкции."
)

# Сообщения для команды /help
HELP_MESSAGE = (
    "📚Справка по командам\n\n"
    "ВСЕ КОМАНДЫ ПИШУТСЯ В РУБЛЯХ, УТОЧНЯТЬ НЕТ НУЖДЫ, СМОТРИТЕ ПРИМЕРЫ\n\n"
    "💳 Как писать расходы и доходы:\n"
    "Расход: -сумма описание\n"
    "Доход: +сумма описание\n\n"
    "Примеры:\n -100 продукты, -50 такси\n"
    "  +50000 зарплата, +1000 возврат\n\n"
    "🔍Команды:\n"
    "/balance — текущий баланс\n"
    "/history [период словом: день, неделя, месяц, год] — история за период\n"
    "   Пример: /history неделя\n"
    "/stats [период словом: день, неделя, месяц, год] — статистика за период\n"
    "/category [название] — статистика по категории\n"
    "/export — экспорт в Excel\n\n"
    "Автоматические категории:\n"
    "— Продукты\n"
    "— Быт\n"
    "— Транспорт\n"
    "— Здоровье\n"
    "— Одежда\n"
    "— Развитие\n"
    "— Подарки\n"
    "— Досуг\n"
    "— Переводы"
)

# Сообщения для команды /balance
BALANCE_MESSAGE = (
    "💰 Ваш текущий баланс:\n\n"
    "+Доходы: {income:.2f} ₽\n"
    "-Расходы: {expenses:.2f} ₽\n"
    "\n"
    "💵 Баланс: {balance:.2f} ₽"
)

# Периоды
PERIOD_DAY = "день"
PERIOD_WEEK = "неделю"
PERIOD_MONTH = "месяц"
PERIOD_YEAR = "год"

# Сообщения для команды /history
HISTORY_HEADER = "📊 История операций за {period}:\n\n"
HISTORY_EMPTY = "📭 История транзакций за {period} пуста"
HISTORY_SUMMARY = (
    "Доход: +{total_income:.2f} руб.\n"
    "Расход: -{total_expenses:.2f} руб.\n\n"
    "Баланс: {balance:.2f} руб.\n\n"
)
HISTORY_DAY_HEADER = "📅 {date}"
HISTORY_TRANSACTION = "{emoji} {amount:.2f} руб. | {description} | {category}\n"
HISTORY_TRANSACTION_GROUP = (
    "{emoji} {amount:.2f} руб. | {description} | {category} [x{count}]\n"
)
HISTORY_PAGINATION = (
    "\nСтраница {current_page}/{total_pages}\n"
    "Используйте /history [период] page=N\n"
    "Периоды: day, week, month, year"
)

# Сообщения об ошибках
ERROR_NOT_STARTED = "Пожалуйста, запустите бота командой /start"
ERROR_GENERAL = "Произошла ошибка. Пожалуйста, попробуйте позже."
ERROR_TRANSACTION = "Произошла ошибка при сохранении транзакции. Пожалуйста, проверьте формат сообщения и попробуйте снова."
ERROR_CATEGORY_NOT_FOUND = "Не удалось найти транзакцию или категорию."
ERROR_INVALID_AMOUNT = "Не удалось распознать сумму. Пожалуйста, проверьте формат."
ERROR_NO_DESCRIPTION = (
    "Пожалуйста, укажите описание транзакции. Например:\n"
    "-100 такси\n"
    "+500 зарплата"
)
ERROR_PROCESSING = "Произошла ошибка при обработке сообщения. Попробуйте снова."
ERROR_BOT = (
    "😔 Произошла ошибка при обработке вашего запроса.\n"
    "Пожалуйста, попробуйте позже или обратитесь к администратору."
)

# Сообщения для подтверждения транзакций
TRANSACTION_SAVED = (
    "Записан {operation_type}: {amount:.2f} руб.\n" "Описание: {description}{category}"
)
CATEGORY_INFO = "\nКатегория: {category_name}"

# Сообщения для статистики
STATS_MESSAGE = (
    "Статистика за {period}:\n\n"
    "Доходы: {income:.2f} руб.\n"
    "Расходы: {expenses:.2f} руб.\n"
    "Баланс: {balance:.2f} руб.\n\n"
    "{categories}"
)

TOP_CATEGORIES_HEADER = "Топ категорий расходов:\n"
TOP_CATEGORY_ITEM = "• {category}: {amount:.2f} руб.\n"

# Сообщения для категорий
CATEGORY_LIST_HEADER = (
    "📋 Список категорий:\n\n💡 Все категории можно вводить с маленькой буквы\n\n"
)
CATEGORY_LIST_ITEM = "• {name}\n"
CATEGORY_LIST_FOOTER = (
    "\nДля просмотра статистики используйте команду:\n/category [название]"
)
CATEGORY_NOT_FOUND = "Категория '{name}' не найдена.\nИспользуйте /category для просмотра списка категорий."
CATEGORY_NO_TRANSACTIONS = "У вас нет транзакций в категории '{name}'"
CATEGORY_STATS = (
    "📊 Статистика по категории '{name}':\n\n"
    " Всего транзакций: {total}\n"
    " Общая сумма: {total_amount:.2f} руб.\n"
    " Средняя сумма: {avg_amount:.2f} руб.\n\n"
    " Расходы: {expenses:.2f} руб. ({expense_count} операций)\n"
    " Доходы: {incomes:.2f} руб. ({income_count} операций)\n\n"
    " Последние операции:\n"
)
CATEGORY_TRANSACTION = "{emoji} {date}: {amount:.2f} руб. - {description}\n"
CATEGORY_NO_CATEGORIES = (
    "В системе пока нет категорий. Администратор может добавить их."
)

# Сообщения для диалога добавления транзакции
ADD_TRANSACTION_START = "Выберите тип транзакции:"
ADD_TRANSACTION_AMOUNT = "Введите сумму {type} (только число):"
ADD_TRANSACTION_DESCRIPTION = "Введите описание транзакции:"
ADD_TRANSACTION_CATEGORY = (
    "Выбрана категория: {category}\nВы можете изменить категорию или подтвердить выбор:"
)
ADD_TRANSACTION_SAVED = (
    "Транзакция добавлена:\n"
    "{sign}{amount} руб.\n"
    "Категория: {category}\n"
    "Описание: {description}"
)
ADD_TRANSACTION_CANCELLED = "Добавление транзакции отменено."
ADD_TRANSACTION_INVALID_AMOUNT = (
    "Пожалуйста, введите корректное число. Попробуйте снова:"
)

# Сообщения для экспорта
EXPORT_EMPTY = "История транзакций пуста"
EXPORT_CAPTION = "📊 История ваших транзакций в Excel"

# Сообщения для изменения категории
CHANGE_CATEGORY_SUCCESS = (
    "Категория изменена:\n"
    "{sign}{amount} руб.\n"
    "Категория: {category}\n"
    "Описание: {description}"
)

# Системные сообщения и ошибки
SYSTEM_ENV_FILE_NOT_FOUND = (
    "Файл .env не найден! Запустите 'python setup_env.py' для его создания."
)
SYSTEM_ENV_FILE_PERMISSIONS = "Небезопасные права доступа к файлу .env: {permissions}. Установите права доступа 600 (chmod 600 .env)"
SYSTEM_ENV_VARS_MISSING = "Отсутствуют необходимые переменные окружения: {vars}"
SYSTEM_TOKEN_NOT_SET = "Не установлен токен бота в переменных окружения"
SYSTEM_INVALID_PERIOD = "Неверный период. Используйте: day, week, month, year"

# Сообщения для логов
LOG_NEW_USER = "Новый пользователь зарегистрирован: {user_id}"
LOG_START_ERROR = "Ошибка в команде /start"
LOG_BALANCE_ERROR = "Ошибка при получении баланса"
LOG_HISTORY_ERROR = "Ошибка при получении истории"
LOG_STATS_ERROR = "Ошибка при получении статистики"
LOG_TOTAL_ERROR = "Ошибка при получении общей статистики"
LOG_CATEGORY_ERROR = "Ошибка при получении статистики по категории"
LOG_EXPORT_ERROR = "Ошибка при экспорте данных"
LOG_UPDATE_ERROR = "Ошибка при обработке обновления {update}: {error}"
LOG_ERROR_MESSAGE_ERROR = "Ошибка при отправке сообщения об ошибке: {error}"
LOG_CATEGORY_CHANGE_ERROR = "Ошибка при изменении категории: {error}"
LOG_TRANSACTION_ERROR = "Ошибка при обработке сообщения о транзакции: {error}"

# Сообщения для экспорта
EXPORT_HEADERS = ["Дата", "Тип", "Сумма", "Описание", "Категория"]
EXPORT_TRANSACTION_TYPE_EXPENSE = "Расход"
EXPORT_TRANSACTION_TYPE_INCOME = "Доход"
CATEGORY_DEFAULT = "Без категории"

# Сообщения для очистки БД
CLEAN_DB_NOT_ADMIN = "У вас нет прав администратора для выполнения этой команды."
CLEAN_DB_CONFIRM = (
    "⚠️ ВНИМАНИЕ! Вы собираетесь удалить все транзакции старше {days} дней.\n"
    "Это действие необратимо!\n\n"
    "Для подтверждения нажмите соответствующую кнопку:"
)
CLEAN_DB_SUCCESS = "🗑 Удалено {count} транзакций старше {days} дней."
CLEAN_DB_CANCELLED = "Очистка БД отменена."
CLEAN_DB_NO_OLD_TRANSACTIONS = "Нет транзакций старше {days} дней для удаления."
