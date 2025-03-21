"""
Обработчики основных команд бота
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import csv
from io import StringIO
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import func
from src.database import SessionLocal
from src.models import User, Transaction, Category, TransactionType
import logging

logger = logging.getLogger(__name__)


class CommandHandlers:
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /start"""
        await update.message.reply_text(
            "Привет! Я бот для учета финансов.\n\n"
            "Формат сообщений:\n"
            "- `-100 продукты` для записи расхода\n"
            "+ `+1000 зарплата` для записи дохода\n\n"
            "Команды:\n"
            "/balance - текущий баланс\n"
            "/history - история транзакций\n"
            "/stats - статистика по категориям\n"
            "/export - выгрузить историю в CSV\n"
            "/help - показать справку"
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /help"""
        await update.message.reply_text(
            "Справка по командам:\n\n"
            "Формат сообщений:\n"
            "- Расход: `-сумма описание`\n"
            "+ Доход: `+сумма описание`\n\n"
            "Примеры:\n"
            "`-100 продукты`\n"
            "`+1000 зарплата`\n"
            "`-50.5 кофе`\n\n"
            "Команды:\n"
            "/balance - текущий баланс\n"
            "/history - история транзакций\n"
            "/stats - статистика по категориям\n"
            "/export - выгрузка в CSV"
        )

    async def balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /balance"""
        user_id = update.effective_user.id
        db = SessionLocal()

        try:
            user = db.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                await update.message.reply_text("У вас пока нет транзакций.")
                return

            # Получаем сумму доходов и расходов
            income = (
                db.query(func.sum(Transaction.amount))
                .filter(
                    Transaction.user_id == user.id,
                    Transaction.type == TransactionType.INCOME,
                )
                .scalar()
                or 0
            )

            expense = (
                db.query(func.sum(Transaction.amount))
                .filter(
                    Transaction.user_id == user.id,
                    Transaction.type == TransactionType.EXPENSE,
                )
                .scalar()
                or 0
            )

            balance = income - expense

            # Формируем сообщение
            await update.message.reply_text(
                f"Баланс: +{income:.2f} | -{expense:.2f} | Итого: {balance:.2f} руб."
            )

        finally:
            db.close()

    def _parse_date_filter(
        self, args: str
    ) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Парсит аргументы для фильтрации по дате"""
        try:
            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

            if not args:
                # По умолчанию показываем последние 10 транзакций
                logger.info("Нет аргументов, возвращаем None")
                return None, None

            original_args = args
            args = args.lower().strip()
            logger.info(f"Парсинг аргумента даты: '{args}'")

            # Убираем предлог "за" если есть
            if args.startswith("за "):
                args = args[3:].strip()
                logger.info(f"Аргумент после удаления 'за': '{args}'")

            # Сначала пробуем распарсить как число
            try:
                days = int(args)
                if days <= 0:
                    logger.warning(
                        f"Получено отрицательное или нулевое количество дней: {days}"
                    )
                    return None, None
                logger.info(f"Успешно распарсили число дней: {days}")
                return now - timedelta(days=days), now
            except ValueError:
                logger.info(
                    f"Аргумент '{args}' не является числом, проверяем другие форматы"
                )

            # Проверяем ключевые слова
            if args in ["сегодня", "день"]:
                logger.info("Выбран период: сегодня")
                return today_start, now
            elif args == "вчера":
                logger.info("Выбран период: вчера")
                return today_start - timedelta(days=1), today_start - timedelta(
                    seconds=1
                )
            elif args == "позавчера":
                logger.info("Выбран период: позавчера")
                return today_start - timedelta(days=2), today_start - timedelta(
                    days=1, seconds=1
                )
            elif args in ["неделю", "неделя"]:
                logger.info("Выбран период: неделя")
                return now - timedelta(days=7), now
            elif args in ["месяц"]:
                logger.info("Выбран период: месяц")
                return now - timedelta(days=30), now
            elif args in ["год"]:
                logger.info("Выбран период: год")
                return now - timedelta(days=365), now

            # Проверяем диапазон дней
            if "-" in args:
                try:
                    start_days, end_days = map(int, args.split("-"))
                    if start_days <= 0 or end_days <= 0:
                        logger.warning(
                            f"Получен некорректный диапазон дней: {start_days}-{end_days}"
                        )
                        return None, None
                    if start_days > end_days:
                        start_days, end_days = end_days, start_days
                    logger.info(
                        f"Выбран период: от {start_days} до {end_days} дней назад"
                    )
                    return now - timedelta(days=end_days), now - timedelta(
                        days=start_days - 1
                    )
                except ValueError:
                    logger.info(f"Не удалось распарсить диапазон дней: '{args}'")

            logger.warning(f"Не удалось распарсить аргумент даты: '{original_args}'")
            return None, None

        except Exception as e:
            logger.error(f"Ошибка при парсинге даты '{args}': {str(e)}", exc_info=True)
            return None, None

    async def history(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /history"""
        user_id = update.effective_user.id
        db = SessionLocal()

        try:
            user = db.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                await update.message.reply_text("У вас пока нет транзакций.")
                return

            # Получаем аргументы команды и логируем их
            logger.info(f"Raw context.args: {context.args}")

            # Проверяем, есть ли аргументы вообще
            if not context.args:
                args = ""
                logger.info("No arguments provided")
            else:
                # Преобразуем список аргументов в строку
                args = " ".join(str(arg) for arg in context.args)
                logger.info(f"Joined args: '{args}'")

            # Логируем входящие параметры
            logger.info(f"История транзакций для user_id={user_id}, args='{args}'")

            try:
                date_start, date_end = self._parse_date_filter(args)
                logger.info(f"Parsed dates: start={date_start}, end={date_end}")
            except Exception as e:
                logger.error(f"Error in _parse_date_filter: {str(e)}", exc_info=True)
                raise

            # Базовый запрос
            query = db.query(Transaction).filter(Transaction.user_id == user.id)

            # Добавляем фильтры по дате если они есть
            if date_start and date_end:
                logger.info(f"Applying date filter: {date_start} - {date_end}")
                query = query.filter(
                    Transaction.created_at >= date_start,
                    Transaction.created_at <= date_end,
                )

            # Получаем транзакции
            transactions = (
                query.order_by(Transaction.created_at.desc())
                .limit(10 if not date_start else None)
                .all()
            )
            logger.info(f"Found {len(transactions)} transactions")

            if not transactions:
                period = ""
                if args:
                    period = f" за период {args}"
                await update.message.reply_text(f"Нет транзакций{period}")
                return

            # Считаем общую статистику
            total_income = sum(
                tx.amount for tx in transactions if tx.type == TransactionType.INCOME
            )
            total_expense = sum(
                tx.amount for tx in transactions if tx.type == TransactionType.EXPENSE
            )
            balance = total_income - total_expense

            # Формируем сообщение
            period = f" за {args}" if args else ""
            message = f"История{period}:\n"
            message += f"(Доход: +{total_income:.2f} | Расход: -{total_expense:.2f} | Баланс: {balance:.2f})\n\n"

            # Загружаем все категории заранее для оптимизации
            categories = {cat.id: cat.name for cat in db.query(Category).all()}

            for tx in transactions:
                sign = "-" if tx.type == TransactionType.EXPENSE else "+"
                # Безопасное получение имени категории
                category_name = categories.get(tx.category_id, "Без категории")
                message += (
                    f"{sign}{tx.amount:.2f} - {tx.description} "
                    f"({category_name}) [{tx.created_at.strftime('%d.%m.%Y %H:%M')}]\n"
                )

            await update.message.reply_text(message)

        except Exception as e:
            logger.error(f"Ошибка в команде history: {str(e)}", exc_info=True)
            logger.error(f"Context args: {context.args}")
            await update.message.reply_text(
                "Не удалось получить историю транзакций. "
                "Проверьте формат команды:\n"
                "/history - последние 10 транзакций\n"
                "/history 4 - за последние 4 дня\n"
                "/history сегодня - за сегодня\n"
                "/history неделя - за неделю"
            )
        finally:
            db.close()

    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /stats"""
        user_id = update.effective_user.id
        db = SessionLocal()

        try:
            user = db.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                await update.message.reply_text("У вас пока нет транзакций.")
                return

            # Получаем статистику по категориям за последний месяц
            month_ago = datetime.now() - timedelta(days=30)

            # Статистика по расходам
            expenses = (
                db.query(Category.name, func.sum(Transaction.amount).label("total"))
                .join(Transaction, Transaction.category_id == Category.id)
                .filter(
                    Transaction.user_id == user.id,
                    Transaction.type == TransactionType.EXPENSE,
                    Transaction.created_at >= month_ago,
                )
                .group_by(Category.name)
                .order_by(func.sum(Transaction.amount).desc())
                .all()
            )

            # Статистика по доходам
            incomes = (
                db.query(Category.name, func.sum(Transaction.amount).label("total"))
                .join(Transaction, Transaction.category_id == Category.id)
                .filter(
                    Transaction.user_id == user.id,
                    Transaction.type == TransactionType.INCOME,
                    Transaction.created_at >= month_ago,
                )
                .group_by(Category.name)
                .order_by(func.sum(Transaction.amount).desc())
                .all()
            )

            # Формируем сообщение
            message = "Статистика за 30 дней:\n\n"

            if expenses:
                message += "Расходы по категориям:\n"
                for category, amount in expenses:
                    message += f"{category}: {amount:.2f} руб.\n"
                message += "\n"

            if incomes:
                message += "Доходы по категориям:\n"
                for category, amount in incomes:
                    message += f"{category}: {amount:.2f} руб.\n"

            if not (expenses or incomes):
                message = "Нет данных за последние 30 дней."

            await update.message.reply_text(message)

        finally:
            db.close()

    async def export(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /export"""
        user_id = update.effective_user.id
        db = SessionLocal()

        try:
            user = db.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                await update.message.reply_text("У вас пока нет транзакций.")
                return

            # Получаем все транзакции пользователя
            transactions = (
                db.query(Transaction)
                .filter(Transaction.user_id == user.id)
                .order_by(Transaction.created_at.desc())
                .all()
            )

            if not transactions:
                await update.message.reply_text("У вас пока нет транзакций.")
                return

            # Создаем CSV файл
            output = StringIO()
            writer = csv.writer(output)

            # Записываем заголовки
            writer.writerow(["Дата", "Тип", "Сумма", "Описание", "Категория"])

            # Записываем транзакции
            for tx in transactions:
                category = db.query(Category).get(tx.category_id)
                writer.writerow(
                    [
                        tx.created_at.strftime("%d.%m.%Y %H:%M"),
                        "Расход" if tx.type == TransactionType.EXPENSE else "Доход",
                        f"{tx.amount:.2f}",
                        tx.description,
                        category.name,
                    ]
                )

            # Отправляем файл
            output.seek(0)
            await update.message.reply_document(
                document=output.getvalue().encode(),
                filename=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
                caption="Ваши транзакции",
            )

        finally:
            db.close()
