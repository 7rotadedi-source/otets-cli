# -*- coding: utf-8 -*-
"""
Терминальный UI для Отец CLI

Красивый вывод постов и навигация
"""

import sys
from typing import List, Dict, Any, Optional
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.markdown import Markdown
from rich.spinner import Spinner
from rich.live import Live
import time

from src.api.client import OtetsAPIClient
from src.utils.errors import OtetsError
from src.utils.parsers import format_timestamp, format_number


class TerminalUI:
    """
    Интерактивный терминальный интерфейс
    """
    
    def __init__(self, api: OtetsAPIClient):
        """
        Инициализация UI
        
        Args:
            api: API клиент
        """
        self.api = api
        self.console = Console(force_terminal=True, record=False)
        
        self.current_page = 0
        self.posts = []
        self.all_posts = []
        self.search_query = None
        self.search_results = []
        
        # Размер страницы
        self.page_size = self.api.limit
        
        # Флаг для выхода
        self.running = True
    
    def run(self):
        """
        Главный цикл приложения
        """
        self._show_welcome()
        
        # Загружаем посты
        self._load_posts()
        
        # Основной цикл
        while self.running:
            self._display_posts()
            self._handle_input()
    
    def _show_welcome(self):
        """
        Показать приветственный экран
        """
        welcome_text = """
🧠 [bold cyan]Отец CLI[/bold cyan] — терминал философии

[yellow]Читаем посты из мудрости прямо в терминал[/yellow]
        """
        
        self.console.print(welcome_text)
        self.console.print(
            Panel(
                "[cyan]Загружаю фонды мудрости...[/cyan]",
                style="bold blue",
                expand=False
            )
        )
    
    def _load_posts(self):
        """
        Загрузить посты из API
        """
        try:
            # Показываем спиннер загрузки
            with self.console.status(
                "[bold cyan]⏳ Загружаю посты мудрости...[/bold cyan]",
                spinner="dots"
            ):
                self.all_posts = self.api.get_user_posts(limit=100)
                self.posts = self.all_posts[:self.page_size]
        
        except OtetsError as e:
            self.console.print(
                f"[bold red]❌ Ошибка: {e}[/bold red]"
            )
            # Используем фейковые посты при ошибке
            self.all_posts = self.api.get_user_posts(limit=100)
            self.posts = self.all_posts[:self.page_size]
    
    def _display_posts(self):
        """
        Показать текущие посты
        """
        self.console.clear()
        self._show_welcome()
        
        if not self.posts:
            self.console.print(
                Panel(
                    "[yellow]Постов не найдено[/yellow]",
                    style="bold red",
                    title="⚠️  Информация"
                )
            )
            return
        
        # Показываем заголовок
        if self.search_query:
            title = f"🔍 Результаты поиска: '{self.search_query}'"
        else:
            title = f"📖 Фонды мудрости Отца"
        
        self.console.print(
            f"\n[bold cyan]{title}[/bold cyan]"
        )
        
        # Показываем каждый пост
        for i, post in enumerate(self.posts, 1):
            self._display_post(post, i)
        
        # Показываем информацию о пагинации
        self._show_pagination_info()
    
    def _display_post(
        self,
        post: Dict[str, Any],
        index: int
    ):
        """
        Показать отдельный пост
        """
        # Извлекаем данные
        post_id = post.get('id', 'N/A')
        text = post.get('text', post.get('content', ''))
        created_at = post.get('created_at', '')
        likes = post.get('likes', 0)
        
        # Форматируем текст
        if isinstance(text, str):
            text = text.strip()[:500]  # Ограничиваем длину
        else:
            text = str(text)
        
        # Форматируем дату
        timestamp = format_timestamp(created_at) if created_at else "недавно"
        
        # Форматируем лайки
        likes_str = format_number(likes) if likes else "0"
        
        # Создаем содержимое поста
        content = f"""
[bold]{text}[/bold]

[dim]{timestamp}  |  ❤️  {likes_str}[/dim]
        """
        
        # Показываем в панели
        panel = Panel(
            content.strip(),
            title=f"Пост #{post_id}",
            title_align="left",
            border_style="cyan" if index % 2 == 0 else "magenta",
            expand=True
        )
        
        self.console.print(panel)
    
    def _show_pagination_info(self):
        """
        Показать информацию о пагинации и командах
        """
        page_num = self.current_page + 1
        total_pages = (len(self.all_posts) + self.page_size - 1) // self.page_size
        
        info_text = f"""
[bold cyan]═══════════════════════════════════════[/bold cyan]
[dim]Страница {page_num} из {total_pages}  |  Всего постов: {len(self.all_posts)}[/dim]

[bold]Команды:[/bold]
  [cyan]n[/cyan] — следующая страница
  [cyan]p[/cyan] — предыдущая страница
  [cyan]s[/cyan] — поиск по ключевому слову
  [cyan]r[/cyan] — перезагрузить
  [cyan]q[/cyan] — выход
[bold cyan]═══════════════════════════════════════[/bold cyan]
        """
        
        self.console.print(info_text)
    
    def _handle_input(self):
        """
        Обработать ввод пользователя
        """
        try:
            command = input("\n[bold yellow]➜[/bold yellow]  ").strip().lower()
            self._process_command(command)
        except EOFError:
            # При Ctrl+D выходим
            self.running = False
    
    def _process_command(self, command: str):
        """
        Обработать команду пользователя
        """
        if command == 'n':
            self._next_page()
        elif command == 'p':
            self._prev_page()
        elif command == 's':
            self._search()
        elif command == 'r':
            self._reload()
        elif command == 'q':
            self.running = False
            self.console.print(
                "\n[bold cyan]✨ Спасибо за внимание к фондам мудрости![/bold cyan]\n"
            )
        else:
            # Игнорируем неизвестные команды
            pass
    
    def _next_page(self):
        """
        Перейти на следующую страницу
        """
        max_pages = (len(self.all_posts) + self.page_size - 1) // self.page_size
        
        if self.current_page + 1 < max_pages:
            self.current_page += 1
            start = self.current_page * self.page_size
            end = start + self.page_size
            self.posts = self.all_posts[start:end]
        else:
            self.console.print(
                "[yellow]⚠️  Вы на последней странице[/yellow]"
            )
            time.sleep(1)
    
    def _prev_page(self):
        """
        Перейти на предыдущую страницу
        """
        if self.current_page > 0:
            self.current_page -= 1
            start = self.current_page * self.page_size
            end = start + self.page_size
            self.posts = self.all_posts[start:end]
        else:
            self.console.print(
                "[yellow]⚠️  Вы на первой странице[/yellow]"
            )
            time.sleep(1)
    
    def _search(self):
        """
        Поиск по ключевому слову
        """
        try:
            query = input(
                "\n[bold cyan]🔍 Введите поисковый запрос:[/bold cyan]  "
            ).strip()
            
            if not query:
                return
            
            self.console.print(
                "[cyan]Ищу посты...[/cyan]"
            )
            
            self.search_query = query
            self.search_results = self.api.search_posts(query)
            
            if self.search_results:
                self.posts = self.search_results
                self.current_page = 0
            else:
                self.console.print(
                    f"[yellow]Постов с '{query}' не найдено[/yellow]"
                )
                time.sleep(2)
        
        except KeyboardInterrupt:
            pass
    
    def _reload(self):
        """
        Перезагрузить посты
        """
        self.console.print(
            "[cyan]Перезагружаю посты...[/cyan]"
        )
        self.current_page = 0
        self.search_query = None
        self.search_results = []
        self._load_posts()
