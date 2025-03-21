"""
Основной файл бота
"""

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from src.config.env import load_environment
from src.handlers.command_handlers import CommandHandlers
from src.handlers.transaction_handlers import TransactionHandlers
from src.handlers.button_handlers import ButtonHandlers
from src.middleware import LoggingMiddleware, MetricsMiddleware
from src.logger import bot_logger

logger = bot_logger


class FinanceBot:
    def __init__(self):
        """Инициализация бота"""
        # Загружаем переменные окружения
        env = load_environment()
        self.token = env["TELEGRAM_BOT_TOKEN"]
        self.admin_ids = env["ADMIN_USER_IDS"]

        # Инициализируем обработчики
        self.command_handlers = CommandHandlers()
        self.transaction_handlers = TransactionHandlers()
        self.button_handlers = ButtonHandlers()

        # Инициализируем middleware
        self.logging_middleware = LoggingMiddleware()
        self.metrics_middleware = MetricsMiddleware()

    def register_handlers(self, application: Application):
        """Регистрация всех обработчиков команд с применением middleware"""

        def wrap_handler(handler):
            async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE):
                async def handler_with_logging(
                    update: Update, context: ContextTypes.DEFAULT_TYPE
                ):
                    return await handler(update, context)

                return await self.metrics_middleware(
                    update,
                    context,
                    lambda u, c: self.logging_middleware(u, c, handler_with_logging),
                )

            return wrapped

        # Регистрируем обработчики команд
        commands = {
            "start": self.command_handlers.start,
            "help": self.command_handlers.help,
            "balance": self.command_handlers.balance,
            "history": self.command_handlers.history,
            "stats": self.command_handlers.stats,
            "export": self.command_handlers.export,
        }

        for command, handler in commands.items():
            application.add_handler(CommandHandler(command, wrap_handler(handler)))

        # Регистрируем обработчик текстовых сообщений
        application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                wrap_handler(self.transaction_handlers.process_transaction_message),
            )
        )

        # Добавляем обработчик для кнопок
        application.add_handler(
            CallbackQueryHandler(wrap_handler(self.button_handlers.handle_button))
        )

        # Регистрируем обработчик ошибок
        application.add_error_handler(self.error_handler)

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        logger.error("Произошла ошибка:", exc_info=context.error)
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Произошла ошибка. Пожалуйста, попробуйте позже."
            )

    def run(self):
        """Запуск бота"""
        try:
            application = Application.builder().token(self.token).build()
            self.register_handlers(application)
            logger.info("Бот запущен")
            application.run_polling()
        except Exception as e:
            logger.error("Ошибка при запуске бота:", exc_info=e)
            raise
