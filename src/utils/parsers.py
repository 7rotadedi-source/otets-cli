# -*- coding: utf-8 -*-
"""
Парсеры и форматеры для Отец CLI
"""

from datetime import datetime
from typing import Optional


def format_timestamp(timestamp: Optional[str]) -> str:
    """
    Форматирует временную метку в читаемый формат
    
    Args:
        timestamp: ISO 8601 строка или объект datetime
    
    Returns:
        Отформатированная строка
    """
    if not timestamp:
        return "неизвестно"
    
    try:
        # Парсим ISO 8601 формат
        if isinstance(timestamp, str):
            # Удаляем суффикс Z если есть
            if timestamp.endswith('Z'):
                timestamp = timestamp[:-1]
            
            dt = datetime.fromisoformat(timestamp)
        else:
            dt = timestamp
        
        # Форматируем
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        diff = now - dt
        
        # Разные диапазоны времени
        if diff.total_seconds() < 60:
            return "только что"
        elif diff.total_seconds() < 3600:
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes}м назад"
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}ч назад"
        elif diff.total_seconds() < 604800:
            days = int(diff.total_seconds() / 86400)
            return f"{days}д назад"
        else:
            return dt.strftime("%d.%m.%Y")
    
    except Exception:
        return str(timestamp)[:10]


def format_number(number: int) -> str:
    """
    Форматирует число в сокращенный вид
    
    Args:
        number: число для форматирования
    
    Returns:
        Отформатированная строка
    """
    if number < 1000:
        return str(number)
    elif number < 1000000:
        return f"{number / 1000:.1f}K".rstrip('0').rstrip('.')
    else:
        return f"{number / 1000000:.1f}M".rstrip('0').rstrip('.')


def truncate_text(text: str, length: int = 100) -> str:
    """
    Обрезает текст до определенной длины
    
    Args:
        text: текст для обрезания
        length: максимальная длина
    
    Returns:
        Обрезанный текст
    """
    if len(text) <= length:
        return text
    return text[:length-3] + "..."


def extract_hashtags(text: str) -> list:
    """
    Извлекает хэштеги из текста
    
    Args:
        text: текст для поиска
    
    Returns:
        Список найденных хэштегов
    """
    import re
    pattern = r'#\w+'
    return re.findall(pattern, text)


def extract_mentions(text: str) -> list:
    """
    Извлекает упоминания из текста
    
    Args:
        text: текст для поиска
    
    Returns:
        Список найденных упоминаний
    """
    import re
    pattern = r'@\w+'
    return re.findall(pattern, text)
