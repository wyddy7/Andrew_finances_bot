#!/bin/bash

echo "Starting Finance Bot..."

# Создаем необходимые директории
mkdir -p data logs

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please edit .env file with your settings"
    exit 1
fi

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Инициализируем базу данных
echo "Initializing database..."
python3 src/init_db.py

# Запускаем бота в фоновом режиме
echo "Starting bot..."
nohup python3 src/run.py > logs/bot.log 2>&1 &
echo $! > bot.pid

echo "Bot is running in background. Check logs/bot.log for details." 