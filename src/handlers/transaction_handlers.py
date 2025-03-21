"""
Обработчики для работы с транзакциями
"""

from datetime import datetime
from typing import Dict, List, Optional
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import func
from src.database import SessionLocal
from src.models import User, Transaction, Category, TransactionType
from src.utils.parsers import parse_transaction_message, determine_category
from src.config.constants import MAX_TRANSACTIONS_PER_10_MIN, TRANSACTION_WINDOW_SECONDS


class TransactionHandlers:
    def __init__(self):
        # Словарь для отслеживания транзакций пользователей
        self.user_transactions: Dict[int, List[datetime]] = {}

    def check_transaction_limit(self, user_id: int) -> bool:
        """
        Проверка лимита транзакций пользователя

        Args:
            user_id: ID пользователя

        Returns:
            bool: True если лимит не превышен, False иначе
        """
        try:
            current_time = datetime.now()
            if user_id not in self.user_transactions:
                self.user_transactions[user_id] = []

            # Удаляем старые транзакции
            self.user_transactions[user_id] = [
                timestamp
                for timestamp in self.user_transactions[user_id]
                if (current_time - timestamp).total_seconds()
                < TRANSACTION_WINDOW_SECONDS
            ]

            # Проверяем количество транзакций
            if len(self.user_transactions[user_id]) >= MAX_TRANSACTIONS_PER_10_MIN:
                return False

            # Добавляем новую транзакцию
            self.user_transactions[user_id].append(current_time)
            return True
        except Exception:
            return False

    async def process_transaction_message(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Обработка сообщений о транзакциях

        Args:
            update: Объект обновления Telegram
            context: Контекст бота
        """
        message = update.message.text.strip()
        user_id = update.effective_user.id

        # Проверяем лимит транзакций
        if not self.check_transaction_limit(user_id):
            await update.message.reply_text(
                "Превышен лимит транзакций (100 транзакций за 10 минут). "
                "Пожалуйста, подождите немного."
            )
            return

        # Парсим сообщение
        result = parse_transaction_message(message)
        if not result:
            return

        amount, description, is_expense = result

        if not description:
            await update.message.reply_text(
                "Пожалуйста, добавьте описание к транзакции."
            )
            return

        # Определяем категорию
        category_name = determine_category(description)

        # Сохраняем транзакцию в базу данных
        db = SessionLocal()
        try:
            # Получаем или создаем пользователя
            user = db.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                user = User(telegram_id=user_id)
                db.add(user)
                db.commit()
                db.refresh(user)

            # Получаем или создаем категорию
            category = (
                db.query(Category)
                .filter(func.lower(Category.name) == func.lower(category_name))
                .first()
            )

            if not category:
                category = Category(name=category_name)
                db.add(category)
                db.commit()
                db.refresh(category)

            # Создаем транзакцию
            transaction_type = (
                TransactionType.EXPENSE if is_expense else TransactionType.INCOME
            )

            transaction = Transaction(
                user_id=user.id,
                amount=amount,
                description=description,
                category_id=category.id,
                type=transaction_type,
                created_at=datetime.now(),
            )

            db.add(transaction)
            db.commit()

            # Формируем ответное сообщение
            sign = "-" if is_expense else "+"
            await update.message.reply_text(
                f"Сохранено: {sign}{amount:.2f} руб. - {description} ({category_name})"
            )

        except Exception as e:
            db.rollback()
            await update.message.reply_text(
                "Произошла ошибка при сохранении транзакции. "
                "Пожалуйста, попробуйте позже."
            )
            raise e
        finally:
            db.close()
