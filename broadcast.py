import sqlite3
import requests
import time
import os
import argparse # Добавляем импорт argparse

# --- НАСТРОЙКИ ---
# ВАЖНО: Вставьте сюда ваш токен бота Telegram
# BOT_TOKEN = "ВАШ_ТЕЛЕГРАМ_БОТ_ТОКЕН" # Токен теперь будет читаться из переменной окружения
# Текст сообщения для отправки - теперь будет передаваться как аргумент
# MESSAGE_TEXT = "Дорогие пользователи, те 3 молодых человека, что пользуются ботом, вынужден вас огорчить новостью: бот закрывается. Мне влетает в копеечку держать месяцами этого бота, а также разрабатывать решения для него у меня совершенно нет времени. Сервер я выключу 13 числа где-то в 10. Если кому-то что-то нужно сохранить для отслеживания, у вас еще есть время."
# Путь к файлу базы данных SQLite (относительно места запуска скрипта)
DATABASE_PATH = os.path.join("data", "finance_bot.db")
# Название таблицы и столбца
TABLE_NAME = "users"
CHAT_ID_COLUMN = "telegram_id"
# Задержка между отправкой сообщений (в секундах) для избежания лимитов Telegram
SEND_DELAY = 0.1
# --- КОНЕЦ НАСТРОЕК ---

def get_chat_ids(db_path, table, column):
    """Извлекает все chat_id из базы данных SQLite."""
    chat_ids = set() # Используем set для автоматической дедупликации
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT {column} FROM {table}")
        rows = cursor.fetchall()
        for row in rows:
            if row[0]: # Убедимся, что ID не пустой
                 chat_ids.add(row[0])
        conn.close()
        print(f"Найдено {len(chat_ids)} уникальных chat_id.")
        return list(chat_ids)
    except sqlite3.Error as e:
        print(f"Ошибка при чтении базы данных SQLite: {e}")
        return []
    except Exception as e:
        print(f"Произошла непредвиденная ошибка при получении chat_id: {e}")
        return []

def send_message(chat_id, text, token):
    """Отправляет сообщение пользователю через Telegram Bot API."""
    url = f"https://api.telegram.org/bot{token}/sendMessage" # Используем токен, переданный в функцию
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML' # Или 'MarkdownV2', если нужно форматирование
    }
    try:
        response = requests.post(url, data=payload, timeout=10) # Таймаут 10 секунд
        response.raise_for_status() # Проверка на HTTP ошибки (4xx, 5xx)
        result = response.json()
        if result.get("ok"):
            # print(f"Сообщение успешно отправлено в чат {chat_id}")
            return True
        else:
            error_code = result.get('error_code')
            description = result.get('description')
            print(f"Ошибка Telegram API для chat_id {chat_id}: [{error_code}] {description}")
            # Частые ошибки: 403 (Forbidden - бот заблокирован пользователем), 400 (Bad Request - chat_id не найден)
            return False
    except requests.exceptions.RequestException as e:
        print(f"Ошибка сети или HTTP при отправке в чат {chat_id}: {e}")
        return False
    except Exception as e:
        print(f"Непредвиденная ошибка при отправке в чат {chat_id}: {e}")
        return False

def broadcast(token, db_path, table, column, message):
    """Основная функция для выполнения рассылки."""
    if not token: # Проверяем, что токен был передан
        print("Ошибка: Токен бота не предоставлен. Убедитесь, что переменная окружения TELEGRAM_BOT_TOKEN установлена и передана в скрипт.")
        return

    if not os.path.exists(db_path):
         print(f"Ошибка: Файл базы данных не найден по пути: {db_path}")
         print(f"Текущая рабочая директория: {os.getcwd()}")
         return

    chat_ids = get_chat_ids(db_path, table, column)

    if not chat_ids:
        print("Chat ID не найдены или произошла ошибка при чтении БД. Рассылка отменена.")
        return

    print(f"\nНачинается рассылка сообщения:")
    print("-----------------------------------------")
    print(message)
    print("-----------------------------------------")
    confirm = input(f"Отправить это сообщение {len(chat_ids)} пользователям? (yes/no): ")

    if confirm.lower() != 'yes':
        print("Рассылка отменена пользователем.")
        return

    print("\nОтправка...")
    success_count = 0
    fail_count = 0
    start_time = time.time()

    for i, chat_id in enumerate(chat_ids):
        if send_message(chat_id, message, token):
            success_count += 1
        else:
            fail_count += 1

        # Печать прогресса каждые 50 сообщений или в конце
        if (i + 1) % 50 == 0 or (i + 1) == len(chat_ids):
             print(f"Прогресс: {i + 1}/{len(chat_ids)} (Успешно: {success_count}, Ошибок: {fail_count})")

        time.sleep(SEND_DELAY) # Задержка

    end_time = time.time()
    total_time = end_time - start_time
    print("\nРассылка завершена.")
    print(f"Всего отправлено: {success_count}")
    print(f"Ошибок отправки: {fail_count}")
    print(f"Затраченное время: {total_time:.2f} секунд")

if __name__ == "__main__":
    # Проверка, установлена ли библиотека requests
    try:
        import requests
    except ImportError:
        print("Ошибка: библиотека 'requests' не установлена.")
        print("Пожалуйста, установите ее: pip install requests")
        exit()

    # Настройка парсера аргументов
    parser = argparse.ArgumentParser(description="Скрипт для массовой рассылки сообщений пользователям Telegram бота.")
    parser.add_argument("message", type=str, help="Текст сообщения для рассылки. Обязательно заключите в кавычки, если сообщение содержит пробелы.")
    args = parser.parse_args()

    # Получаем токен из переменной окружения
    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not telegram_bot_token:
        print("Ошибка: Переменная окружения TELEGRAM_BOT_TOKEN не найдена или пуста.")
        print("Пожалуйста, установите ее перед запуском скрипта.")
        print("Пример для Linux/macOS: export TELEGRAM_BOT_TOKEN=\"ваш_токен\"")
        print("Пример для Windows PowerShell: $env:TELEGRAM_BOT_TOKEN=\"ваш_токен\"")
        exit()

    broadcast(telegram_bot_token, DATABASE_PATH, TABLE_NAME, CHAT_ID_COLUMN, args.message) # Используем args.message 
