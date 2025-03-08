#!/bin/bash
# Скрипт для первичной настройки сервера Timeweb

# Переменные
SERVER_USER=${1:-"root"}
SERVER_HOST=${2:-"your_server_ip"}

echo "🚀 Начинаем настройку сервера $SERVER_USER@$SERVER_HOST"

# Подключаемся к серверу и выполняем настройку
ssh $SERVER_USER@$SERVER_HOST << 'EOF'
    # Обновляем систему
    echo "📦 Обновляем систему..."
    apt update
    apt upgrade -y
    
    # Устанавливаем необходимые пакеты
    echo "🔧 Устанавливаем необходимые пакеты..."
    apt install -y git curl wget htop net-tools lsb-release

    # Собираем информацию о системе
    echo "🔍 Собираем информацию о системе..."
    echo "=== Информация о системе ===" > system_info.txt
    echo "Дата: $(date)" >> system_info.txt
    echo "" >> system_info.txt
    
    echo "--- Операционная система ---" >> system_info.txt
    echo "Kernel:" >> system_info.txt
    uname -a >> system_info.txt
    echo "Distribution:" >> system_info.txt
    lsb_release -a 2>/dev/null >> system_info.txt
    echo "" >> system_info.txt
    
    echo "--- Процессор ---" >> system_info.txt
    lscpu | grep -E "^CPU\(s\)|Core|Model name" >> system_info.txt
    echo "" >> system_info.txt
    
    echo "--- Память ---" >> system_info.txt
    free -h >> system_info.txt
    echo "" >> system_info.txt
    
    echo "--- Диски ---" >> system_info.txt
    df -h >> system_info.txt
    echo "" >> system_info.txt
    
    echo "--- Сеть ---" >> system_info.txt
    ifconfig >> system_info.txt
    echo "" >> system_info.txt
    
    # Устанавливаем Docker
    echo "🐳 Устанавливаем Docker..."
    if ! command -v docker &> /dev/null; then
        curl -fsSL https://get.docker.com | sh
        apt install -y docker-compose
        systemctl enable docker
        systemctl start docker
    else
        echo "Docker уже установлен"
    fi
    
    # Создаем директорию для проекта
    echo "📁 Создаем директории..."
    mkdir -p /opt/finance_bot/{data,logs,backup}
    chmod 755 /opt/finance_bot /opt/finance_bot/data /opt/finance_bot/logs /opt/finance_bot/backup
    
    # Настраиваем firewall
    echo "🛡️ Настраиваем firewall..."
    apt install -y ufw
    ufw allow ssh
    ufw allow http
    ufw allow https
    ufw --force enable
    
    # Устанавливаем часовой пояс
    echo "🕒 Настраиваем часовой пояс..."
    timedatectl set-timezone Europe/Moscow
    
    # Добавляем информацию о безопасности
    echo "--- Безопасность ---" >> system_info.txt
    echo "Firewall status:" >> system_info.txt
    ufw status >> system_info.txt
    echo "" >> system_info.txt
    echo "Docker status:" >> system_info.txt
    systemctl status docker | head -n 3 >> system_info.txt
    echo "" >> system_info.txt
    
    echo "✅ Настройка сервера завершена!"
    echo "🔍 Статус служб:"
    echo "Docker: $(systemctl is-active docker)"
    echo "UFW: $(ufw status)"
    echo "Timezone: $(timedatectl | grep "Time zone")"
    
    echo "📝 Информация о системе сохранена в файл /opt/finance_bot/system_info.txt"
    mv system_info.txt /opt/finance_bot/
EOF

echo "🎉 Готово! Сервер настроен и готов к деплою"
echo "⚡ Теперь можно:"
echo "1. Проверить информацию о сервере:"
echo "   ssh $SERVER_USER@$SERVER_HOST 'cat /opt/finance_bot/system_info.txt'"
echo "2. Запустить деплой командой:"
echo "   ./scripts/deploy.sh $SERVER_USER $SERVER_HOST" 