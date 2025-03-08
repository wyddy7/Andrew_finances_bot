@echo off
cd /d "%~dp0.."
echo Starting Finance Bot...

REM Создаем необходимые директории
if not exist "data" mkdir data
if not exist "logs" mkdir logs

REM Проверяем наличие виртуального окружения
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Активируем виртуальное окружение
call "%~dp0..\venv\Scripts\activate.bat"

REM Проверяем, нужно ли установить зависимости
if not exist "venv\Lib\site-packages\python_telegram_bot" (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Инициализируем базу данных
echo Initializing database...
python "%~dp0..\src\init_db.py"

REM Запускаем бота
echo Starting bot...
python "%~dp0..\src\run.py"

pause 