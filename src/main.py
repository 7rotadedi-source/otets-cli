#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отец CLI - главная точка входа

Развивает философию через терминал
"""

import sys
import os
from pathlib import Path

# Добавляем корневую папку в PATH для импортов
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.client import OtetsAPIClient
from src.ui.display import TerminalUI
from src.utils.errors import OtetsError
import traceback


def main():
    """
    Главная функция приложения
    """
    try:
        # Инициализируем API клиент
        api = OtetsAPIClient()
        
        # Инициализируем UI
        ui = TerminalUI(api)
        
        # Запускаем интерактивный режим
        ui.run()
        
    except OtetsError as e:
        print(f"\n❌ Ошибка Отца: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n\n👋 Выход из фондов Отца...")
        return 0
    except Exception as e:
        print(f"\n💥 Неожиданная ошибка: {e}")
        traceback.print_exc()
        return 2
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
