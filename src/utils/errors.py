# -*- coding: utf-8 -*-
"""
Пользовательские исключения для Отец CLI
"""


class OtetsError(Exception):
    """
    Базовое исключение для всех ошибок приложения
    """
    pass


class NetworkError(OtetsError):
    """
    Ошибка при работе с сетью
    """
    pass


class NotFoundError(OtetsError):
    """
    Ресурс не найден
    """
    pass


class ServerError(OtetsError):
    """
    Ошибка на стороне сервера
    """
    pass


class ValidationError(OtetsError):
    """
    Ошибка валидации данных
    """
    pass


class ConfigurationError(OtetsError):
    """
    Ошибка конфигурации
    """
    pass
