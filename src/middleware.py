from typing import Any, Awaitable, Callable, Dict, Optional
from telegram import Update
from telegram.ext import ContextTypes
import json
import time
from datetime import datetime
from src.logger import bot_logger, metrics_logger
from collections import defaultdict


class LoggingMiddleware:
    """Middleware для логирования всех входящих обновлений и ответов бота"""

    async def __call__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        handler: Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[Any]],
    ) -> Any:
        start_time = time.time()

        # Подготовка данных для логирования
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "update_id": update.update_id if update else None,
            "chat_id": (
                update.effective_chat.id if update and update.effective_chat else None
            ),
            "user_id": (
                update.effective_user.id if update and update.effective_user else None
            ),
            "username": (
                update.effective_user.username
                if update and update.effective_user
                else None
            ),
            "handler": handler.__name__,
            "message_type": self._get_update_type(update),
            "message_text": self._get_message_text(update),
        }

        try:
            # Логируем входящее сообщение
            bot_logger.info(
                f"Incoming update: {json.dumps(log_data, ensure_ascii=False)}"
            )

            # Выполняем обработчик
            result = await handler(update, context)

            # Добавляем информацию о времени выполнения
            execution_time = time.time() - start_time
            log_data["execution_time"] = f"{execution_time:.3f}s"
            log_data["status"] = "success"

            # Логируем успешное выполнение
            bot_logger.info(
                f"Handler completed: {json.dumps(log_data, ensure_ascii=False)}"
            )

            return result

        except Exception as e:
            # В случае ошибки логируем детали исключения
            execution_time = time.time() - start_time
            log_data["execution_time"] = f"{execution_time:.3f}s"
            log_data["status"] = "error"
            log_data["error"] = str(e)
            log_data["error_type"] = type(e).__name__

            bot_logger.error(
                f"Handler failed: {json.dumps(log_data, ensure_ascii=False)}",
                exc_info=True,
            )
            raise

    def _get_update_type(self, update: Update) -> str:
        """Определяет тип обновления"""
        if update.message:
            return "message"
        elif update.edited_message:
            return "edited_message"
        elif update.callback_query:
            return "callback_query"
        elif update.inline_query:
            return "inline_query"
        return "unknown"

    def _get_message_text(self, update: Update) -> Optional[str]:
        """Извлекает текст сообщения из обновления"""
        if update.message and update.message.text:
            return update.message.text
        elif update.callback_query and update.callback_query.data:
            return update.callback_query.data
        elif update.inline_query and update.inline_query.query:
            return update.inline_query.query
        return None


class MetricsMiddleware:
    """Middleware для сбора метрик производительности"""

    def __init__(self):
        self.metrics: Dict[str, Dict[str, float]] = {}

    async def __call__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        handler: Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[Any]],
    ) -> Any:
        handler_name = handler.__name__
        start_time = time.time()

        try:
            result = await handler(update, context)
            execution_time = time.time() - start_time

            # Обновляем метрики
            if handler_name not in self.metrics:
                self.metrics[handler_name] = {
                    "total_calls": 0,
                    "total_time": 0,
                    "avg_time": 0,
                    "min_time": float("inf"),
                    "max_time": 0,
                }

            stats = self.metrics[handler_name]
            stats["total_calls"] += 1
            stats["total_time"] += execution_time
            stats["avg_time"] = stats["total_time"] / stats["total_calls"]
            stats["min_time"] = min(stats["min_time"], execution_time)
            stats["max_time"] = max(stats["max_time"], execution_time)

            # Логируем метрики
            metrics_logger.info(
                f"Handler metrics - {handler_name}: "
                f"calls={stats['total_calls']}, "
                f"avg_time={stats['avg_time']:.3f}s, "
                f"min_time={stats['min_time']:.3f}s, "
                f"max_time={stats['max_time']:.3f}s"
            )

            return result

        except Exception:
            execution_time = time.time() - start_time
            metrics_logger.error(
                f"Handler failed - {handler_name}: time={execution_time:.3f}s",
                exc_info=True,
            )
            raise


class RateLimitMiddleware:
    """Middleware для ограничения количества операций"""

    def __init__(self, max_operations: int = 100, time_window: int = 600):
        self.max_operations = max_operations  # Максимум 100 операций
        self.time_window = time_window  # За 10 минут (600 секунд)
        self.user_operations = defaultdict(list)

    async def __call__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        handler: Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[Any]],
    ) -> Any:
        if not update.effective_user:
            return await handler(update, context)

        user_id = update.effective_user.id
        current_time = time.time()

        # Очистка старых операций
        self.user_operations[user_id] = [
            op_time
            for op_time in self.user_operations[user_id]
            if current_time - op_time < self.time_window
        ]

        # Проверка лимита
        if len(self.user_operations[user_id]) >= self.max_operations:
            await update.effective_message.reply_text(
                "Превышен лимит операций. Пожалуйста, подождите несколько минут."
            )
            return None

        # Добавление новой операции
        self.user_operations[user_id].append(current_time)

        return await handler(update, context)
