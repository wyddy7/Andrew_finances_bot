"""
Модуль для парсинга сообщений пользователя
"""

import re
from typing import Tuple, Optional
from src.config.constants import EXPENSE_PATTERN, INCOME_PATTERN
from src.config.category_keywords import CATEGORY_KEYWORDS, CATEGORY_DEFAULT


def parse_amount(amount_str: str) -> float:
    """
    Парсинг суммы с учетом пробелов и других символов

    Args:
        amount_str: Строка с суммой

    Returns:
        float: Распарсенная сумма

    Raises:
        ValueError: Если не удалось распарсить сумму
    """
    # Удаляем все нецифровые символы, кроме точки, запятой и пробелов
    clean_str = "".join(c for c in amount_str if c.isdigit() or c in "., ")
    # Удаляем все пробелы
    clean_str = clean_str.replace(" ", "")
    # Заменяем запятую на точку
    clean_str = clean_str.replace(",", ".")
    return float(clean_str)


def split_message(message: str) -> Tuple[str, str]:
    """
    Разделяет сообщение на сумму и описание

    Args:
        message: Сообщение пользователя

    Returns:
        tuple: (сумма в виде строки, описание)
    """
    # Пропускаем знак +/- в начале
    message = message[1:].strip()

    # Ищем первое слово, которое не является частью суммы
    parts = message.split()
    amount_parts = []
    description_parts = []

    for part in parts:
        # Если часть содержит цифры или является обозначением валюты
        if any(c.isdigit() for c in part) or part.lower() in [
            "руб",
            "руб.",
            "р.",
            "рублей",
        ]:
            amount_parts.append(part)
        else:
            description_parts.append(part)
            break

    # Добавляем оставшиеся части к описанию
    description_parts.extend(parts[len(amount_parts) + len(description_parts) :])

    return " ".join(amount_parts), " ".join(description_parts)


def determine_category(description: str) -> str:
    """
    Определение категории по описанию

    Args:
        description: Описание транзакции

    Returns:
        str: Название категории
    """
    description_lower = description.lower()

    # Сначала проверяем специальные случаи
    if "8 марта" in description_lower:
        return "Подарки"

    # Затем проверяем обычные ключевые слова
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword.lower() in description_lower for keyword in keywords):
            return category
    return CATEGORY_DEFAULT


def parse_transaction_message(message: str) -> Optional[Tuple[float, str, bool]]:
    """
    Парсинг сообщения о транзакции

    Args:
        message: Сообщение пользователя

    Returns:
        Optional[Tuple[float, str, bool]]: (сумма, описание, признак расхода) или None,
        если сообщение не является транзакцией
    """
    message = message.strip()

    # Определяем тип транзакции
    is_expense = message.startswith("-")
    is_income = message.startswith("+")

    if not (is_expense or is_income):
        return None

    # Выбираем паттерн в зависимости от типа
    pattern = EXPENSE_PATTERN if is_expense else INCOME_PATTERN
    match = re.match(pattern, message)

    if not match:
        return None

    amount_str, description = match.groups()

    try:
        amount = parse_amount(amount_str)
        return amount, description.strip(), is_expense
    except ValueError:
        return None
