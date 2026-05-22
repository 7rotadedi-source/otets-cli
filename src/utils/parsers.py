"""
Парсеры для обработки текста и контента
"""

import re
from typing import List


def clean_html(text: str) -> str:
    """Удалить HTML теги из текста"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def truncate_text(text: str, max_length: int = 200) -> str:
    """Обрезать текст до максимальной длины"""
    if len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text


def extract_urls(text: str) -> List[str]:
    """Извлечь URL из текста"""
    url_pattern = r'https?://[^\s]+'
    return re.findall(url_pattern, text)


def format_timestamp(timestamp: str) -> str:
    """Форматировать временную метку"""
    # Простая форматирование, можно расширить
    if isinstance(timestamp, str) and len(timestamp) > 10:
        return timestamp[:10]  # Показываем только дату
    return timestamp
