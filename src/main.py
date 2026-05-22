#!/usr/bin/env python3
"""
Отец CLI - клиент для чтения постов прямо из терминала
"""

import sys
import os
from dotenv import load_dotenv
from rich.console import Console

from api.client import OtetsAPI
from ui.display import TerminalUI
from utils.errors import OtetsError

# Загружаем переменные окружения
load_dotenv()

console = Console()


def main():
    """Главная точка входа"""
    try:
        # Проверяем конфигурацию
        base_url = os.getenv("OTETS_BASE_URL", "https://xn--d1ah4a.com")
        username = os.getenv("OTETS_USERNAME", "")
        
        if not username:
            console.print(
                "[bold red]❌ Ошибка:[/bold red] Не установлена переменная OTETS_USERNAME",
                highlight=False
            )
            console.print(
                "[yellow]Скопируй .env.example в .env и заполни данные[/yellow]",
                highlight=False
            )
            sys.exit(1)
        
        # Инициализируем API
        api = OtetsAPI(base_url=base_url, username=username)
        
        # Инициализируем UI
        ui = TerminalUI(api)
        
        # Запускаем интерактивный режим
        ui.run()
        
    except OtetsError as e:
        console.print(f"[bold red]❌ Ошибка ИТД:[/bold red] {e}", highlight=False)
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]⏹️  Выход[/yellow]", highlight=False)
        sys.exit(0)
    except Exception as e:
        console.print(
            f"[bold red]❌ Неожиданная ошибка:[/bold red] {e}",
            highlight=False
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
