"""
Пользовательские исключения для обработки ошибок
"""


class OtetsError(Exception):
    """Базовое исключение для ошибок ИТД"""
    pass


class NetworkError(OtetsError):
    """Ошибка сетевого соединения"""
    pass


class APIError(OtetsError):
    """Ошибка API"""
    pass


class ConfigError(OtetsError):
    """Ошибка конфигурации"""
    pass
