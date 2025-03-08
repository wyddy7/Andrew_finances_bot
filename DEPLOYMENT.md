# Руководство по деплою Финансового Бота

В этом документе описаны шаги для развертывания бота на сервере.

## Подготовка к деплою

### Локальная настройка

1. Убедитесь, что на вашем компьютере установлены:

    - Git
    - SSH клиент (OpenSSH или PuTTY)

2. Клонируйте репозиторий, если это еще не сделано:
    ```bash
    git clone <адрес-репозитория>
    cd counter
    ```

### Подготовка сервера

На сервере должны быть установлены:

1. Docker
2. Docker Compose

Если их нет, установите командой:

```bash
curl -fsSL https://get.docker.com | sh
apt-get update && apt-get install -y docker-compose
```

## Методы деплоя

### Метод 1: Автоматический деплой с помощью скрипта

#### Для Linux/Mac:

```bash
./scripts/deploy.sh <пользователь> <адрес-сервера>
```

#### Для Windows:

```cmd
scripts\deploy.bat <пользователь> <адрес-сервера>
```

Замените `<пользователь>` и `<адрес-сервера>` на ваши данные.

### Метод 2: Ручной деплой

1. Создайте архив проекта:

    ```bash
    git archive --format=tar.gz -o deploy.tar.gz HEAD
    ```

2. Скопируйте архив на сервер:

    ```bash
    scp deploy.tar.gz user@server:/tmp/
    ```

3. На сервере:

    ```bash
    # Создайте директорию для проекта
    mkdir -p /opt/finance_bot
    cd /opt/finance_bot

    # Создайте необходимые директории
    mkdir -p data logs backup
    chmod 755 data logs backup

    # Распакуйте архив
    tar -xzf /tmp/deploy.tar.gz -C /opt/finance_bot

    # Создайте .env файл из примера
    cp .env.example .env

    # Настройте .env файл (важно!)
    nano .env

    # Запустите контейнеры
    docker-compose up -d --build
    ```

## Настройка .env файла

Обязательно настройте следующие параметры в .env файле:

-   `TELEGRAM_BOT_TOKEN` - получите у [@BotFather](https://t.me/BotFather)
-   `ADMIN_USER_IDS` - ID администраторов (получите у [@userinfobot](https://t.me/userinfobot))

## Проверка работы

После деплоя убедитесь, что бот работает:

1. Проверьте создание необходимых файлов и директорий:

    ```bash
    ls -la data/ logs/ backup/
    ```

2. Проверьте логи контейнера:

    ```bash
    docker-compose logs -f bot
    ```

3. Откройте Telegram и начните диалог с вашим ботом.

## Обслуживание

### Обновление бота

Для обновления бота повторите процесс деплоя или выполните:

```bash
cd /opt/finance_bot
git pull
docker-compose down
docker-compose up -d --build
```

### Резервное копирование

Для создания резервной копии базы данных:

```bash
# Остановите бота
docker-compose down

# Создайте резервную копию с датой
backup_file="backup/finance_$(date +%Y%m%d_%H%M%S).db"
cp data/finance.db "$backup_file"
echo "Создана резервная копия: $backup_file"

# Запустите бота
docker-compose up -d
```

### Восстановление из резервной копии

Для восстановления базы данных из резервной копии:

```bash
# Остановите бота
docker-compose down

# Сделайте копию текущей базы на всякий случай
cp data/finance.db data/finance.db.old

# Восстановите из бэкапа (замените дату на нужную)
cp backup/finance_YYYYMMDD_HHMMSS.db data/finance.db

# Запустите бота
docker-compose up -d
```

### Мониторинг

Для просмотра логов:

```bash
docker-compose logs -f
```

Для проверки статуса контейнера:

```bash
docker-compose ps
```

## Устранение неполадок

1. **Бот не отвечает:**

    - Проверьте логи: `docker-compose logs -f bot`
    - Убедитесь, что токен бота правильный
    - Проверьте наличие файла базы данных: `ls -l data/finance.db`
    - Проверьте права доступа: `ls -la data/`

2. **Проблемы с базой данных:**

    - Проверьте права доступа к директории data/: `chmod 755 data/`
    - Убедитесь, что файл базы данных не поврежден
    - При необходимости восстановите из резервной копии

3. **Ошибки в контейнере:**

    - Проверьте статус контейнеров: `docker-compose ps`
    - Проверьте использование ресурсов: `docker stats`
    - Перезапустите контейнеры: `docker-compose restart`

4. **Проблемы с правами доступа:**
    ```bash
    # Исправление прав доступа к директориям
    chmod 755 data logs backup
    chown -R 1000:1000 data logs backup  # 1000 - стандартный uid в контейнере
    ```
