FROM python:3.9-slim
WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование .env файла отдельно и установка прав
COPY .env .
RUN chmod 600 .env

# Копирование остального кода
COPY . .

# Создание директорий для логов и данных
RUN mkdir -p logs data

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Запуск приложения
CMD ["python", "src/run.py"]
FROM python:3.9-slim
WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание директорий для логов и данных
RUN mkdir -p logs data

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Запуск приложения
CMD ["python", "src/run.py"]
FROM python:3.9-slim
WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание директорий для логов и данных
RUN mkdir -p logs data

# Переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Инициализация базы данных и запуск бота
CMD python src/init_db.py && python src/run.py
