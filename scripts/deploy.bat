@echo off
REM Скрипт для деплоя на сервер (Windows)

set SERVER_USER=%1
if "%SERVER_USER%"=="" set SERVER_USER=root

set SERVER_HOST=%2
if "%SERVER_HOST%"=="" set SERVER_HOST=your_server_ip

set PROJECT_NAME=finance_bot
set DEPLOY_DIR=/opt/%PROJECT_NAME%

echo 🚀 Начинаем деплой на сервер %SERVER_USER%@%SERVER_HOST%

REM Создаем архив проекта
echo 📦 Создаем архив проекта...
git archive --format=tar.gz -o deploy.tar.gz HEAD

REM Копируем архив на сервер (требуется установленный OpenSSH или PuTTY в PATH)
echo 📤 Копируем архив на сервер...
scp deploy.tar.gz %SERVER_USER%@%SERVER_HOST%:/tmp/

REM Команды на сервере
echo 🔧 Настраиваем окружение на сервере...
ssh %SERVER_USER%@%SERVER_HOST% "mkdir -p %DEPLOY_DIR% && cd %DEPLOY_DIR% && mkdir -p data logs backup && chmod 755 data logs backup && tar -xzf /tmp/deploy.tar.gz -C %DEPLOY_DIR% && if [ ! -f .env ]; then cp .env.example .env; echo '⚠️ Создан .env файл из примера. Не забудьте настроить его!'; fi && if [ -f data/finance.db ]; then backup_file='backup/finance_'$(date +%%Y%%m%%d_%%H%%M%%S)'.db'; cp data/finance.db $backup_file; echo '📑 Создана резервная копия базы данных: '$backup_file; fi && docker-compose down && docker-compose up -d --build && chown -R 1000:1000 data logs backup && echo '✅ Деплой завершен успешно!' && echo '🔍 Проверьте логи командой: docker-compose logs -f bot'"

REM Удаляем локальный архив
del deploy.tar.gz

echo 🎉 Готово! Бот запущен на сервере %SERVER_HOST%
echo ⚠️ Не забудьте настроить .env файл на сервере, если это первый деплой! 