"""
Обработчики для работы с кнопками
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.database import SessionLocal
from src.models import Category


class ButtonHandlers:
    async def handle_button(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Обработчик нажатий на кнопки

        Args:
            update: Объект обновления Telegram
            context: Контекст бота
        """
        query = update.callback_query
        await query.answer()

        # Получаем данные из callback_data
        data = query.data
        if not data:
            return

        # Обрабатываем различные типы кнопок
        if data.startswith("category_"):
            await self._handle_category_button(query, data[9:])
        elif data == "cancel":
            await self._handle_cancel_button(query)

    async def _handle_category_button(
        self, query: Update.callback_query, category_id: str
    ) -> None:
        """
        Обработчик кнопок выбора категории

        Args:
            query: Объект callback query
            category_id: ID категории
        """
        db = SessionLocal()
        try:
            category = db.query(Category).get(int(category_id))
            if category:
                await query.message.edit_text(f"✅ Выбрана категория: {category.name}")
            else:
                await query.message.edit_text("❌ Категория не найдена")
        finally:
            db.close()

    async def _handle_cancel_button(self, query: Update.callback_query) -> None:
        """
        Обработчик кнопки отмены

        Args:
            query: Объект callback query
        """
        await query.message.edit_text("❌ Действие отменено")

    def get_category_keyboard(self, categories: list[Category]) -> InlineKeyboardMarkup:
        """
        Создает клавиатуру с кнопками категорий

        Args:
            categories: Список категорий

        Returns:
            InlineKeyboardMarkup: Клавиатура с кнопками
        """
        keyboard = []
        row = []

        for i, category in enumerate(categories):
            row.append(
                InlineKeyboardButton(
                    category.name, callback_data=f"category_{category.id}"
                )
            )

            # Добавляем по 2 кнопки в ряд
            if len(row) == 2 or i == len(categories) - 1:
                keyboard.append(row)
                row = []

        # Добавляем кнопку отмены
        keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel")])

        return InlineKeyboardMarkup(keyboard)
