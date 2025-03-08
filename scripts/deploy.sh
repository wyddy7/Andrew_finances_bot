#!/bin/bash
# Скрипт для деплоя на сервер

# Остановить скрипт при любой ошибке
set -e

# Переменные
SERVER_USER=${1:-"root"}
SERVER_HOST=${2:-"your_server_ip"}
PROJECT_NAME="finance_bot"
DEPLOY_DIR="/opt/$PROJECT_NAME"

echo "🚀 Начинаем деплой на сервер $SERVER_USER@$SERVER_HOST"

# Создаем архив проекта
echo "📦 Создаем архив проекта..."
git archive --format=tar.gz -o deploy.tar.gz HEAD

# Копируем архив на сервер
echo "📤 Копируем архив на сервер..."
scp deploy.tar.gz $SERVER_USER@$SERVER_HOST:/tmp/

# Команды на сервере
echo "🔧 Настраиваем окружение на сервере..."
ssh $SERVER_USER@$SERVER_HOST << EOF
    # Создаем директорию для проекта, если её нет
    mkdir -p $DEPLOY_DIR
    cd $DEPLOY_DIR
    
    # Создаем необходимые директории
    mkdir -p data logs backup
    chmod 755 data logs backup
    
    # Распаковываем архив
    tar -xzf /tmp/deploy.tar.gz -C $DEPLOY_DIR
    
    # Проверяем наличие Docker и Docker Compose
    if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker или Docker Compose не установлены"
        echo "Установите их командой:"
        echo "curl -fsSL https://get.docker.com | sh && apt-get install -y docker-compose"
        exit 1
    fi
    
    # Проверяем наличие .env файла, если нет - копируем пример
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "⚠️ Создан .env файл из примера. Не забудьте настроить его!"
    fi
    
    # Останавливаем старые контейнеры
    docker-compose down
    
    # Делаем бэкап базы, если она существует
    if [ -f data/finance.db ]; then
        backup_file="backup/finance_\$(date +%Y%m%d_%H%M%S).db"
        cp data/finance.db "\$backup_file"
        echo "📑 Создана резервная копия базы данных: \$backup_file"
    fi
    
    # Запускаем контейнеры
    docker-compose up -d --build
    
    # Исправляем права доступа
    chown -R 1000:1000 data logs backup
    
    echo "✅ Деплой завершен успешно!"
    echo "🔍 Проверьте логи командой: docker-compose logs -f bot"
EOF

# Удаляем локальный архив
rm deploy.tar.gz

echo "🎉 Готово! Бот запущен на сервере $SERVER_HOST"
echo "⚠️ Не забудьте настроить .env файл на сервере, если это первый деплой!" 