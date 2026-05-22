"""
Терминальный интерфейс для отображения постов
"""

from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.align import Align
from rich.prompt import Prompt

from api.client import OtetsAPI, Post
from utils.errors import NetworkError, OtetsError


class TerminalUI:
    """Интерактивный UI для терминала"""
    
    def __init__(self, api: OtetsAPI):
        self.api = api
        self.console = Console()
        self.posts: List[Post] = []
        self.current_page = 0
        self.posts_per_page = 5
        self.username = api.username
        
    def run(self):
        """Запустить интерактивный режим"""
        self._show_welcome()
        
        while True:
            try:
                # Загружаем посты если нужно
                if not self.posts:
                    self._load_posts()
                
                # Показываем текущую страницу
                self._display_page()
                
                # Ждем команду от пользователя
                command = self._get_command()
                
                if not self._handle_command(command):
                    break
                    
            except KeyboardInterrupt:
                break
            except NetworkError as e:
                self.console.print(
                    f"[bold red]❌ Ошибка сети:[/bold red] {e}",
                    highlight=False
                )
                if not self._retry_prompt():
                    break
            except OtetsError as e:
                self.console.print(
                    f"[bold red]❌ Ошибка:[/bold red] {e}",
                    highlight=False
                )
                break
    
    def _show_welcome(self):
        """Показать приветствие"""
        title = Text("🎭 Отец CLI", style="bold cyan", justify="center")
        subtitle = Text(f"Читаем посты {self.username}", style="dim yellow")
        
        welcome_text = f"""
[bold cyan]Постоянное присутствие[/bold cyan] философии в твоем терминале

[yellow]Команды:[/yellow]
  [green]n[/green] - следующая страница
  [green]p[/green] - предыдущая страница
  [green]s[/green] - поиск по ключевому слову
  [green]r[/green] - перезагрузить посты
  [green]q[/green] - выход

[dim]Используй стрелки вверх/вниз для навигации (при поддержке терминала)[/dim]
"""
        
        panel = Panel(
            welcome_text,
            title=title,
            subtitle=subtitle,
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(panel)
    
    def _load_posts(self):
        """Загрузить посты с API"""
        with self.console.status("[bold cyan]⏳ Загружаем посты...", spinner="dots"):
            self.posts = self.api.get_profile_posts(
                username=self.username,
                limit=50  # Загружаем сразу побольше для пагинации
            )
        
        if not self.posts:
            self.console.print(
                "[yellow]⚠️  П��стов не найдено[/yellow]",
                highlight=False
            )
        else:
            self.console.print(
                f"[green]✓ Загружено {len(self.posts)} постов[/green]",
                highlight=False
            )
    
    def _display_page(self):
        """Показать текущую страницу постов"""
        if not self.posts:
            return
        
        # Вычисляем границы текущей страницы
        start = self.current_page * self.posts_per_page
        end = start + self.posts_per_page
        page_posts = self.posts[start:end]
        
        # Если страница пустая, возвращаемся на первую
        if not page_posts and self.current_page > 0:
            self.current_page = 0
            self._display_page()
            return
        
        # Очищаем экран и показываем посты
        self.console.clear()
        
        # Заголовок
        total_pages = (len(self.posts) + self.posts_per_page - 1) // self.posts_per_page
        header = Text(
            f"Посты {self.username} (стр. {self.current_page + 1}/{total_pages})",
            style="bold cyan"
        )
        self.console.print(header)
        self.console.print("[dim]" + "─" * 80 + "[/dim]")
        
        # Показываем посты
        for i, post in enumerate(page_posts, 1):
            self._display_post(post, i)
            
        self.console.print("[dim]" + "─" * 80 + "[/dim]")
        
        # Пагинация
        nav_text = f"[dim]← P[/dim] | [bold cyan]Стр. {self.current_page + 1}/{total_pages}[/bold cyan] | [dim]N →[/dim]"
        self.console.print(Align.center(nav_text))
    
    def _display_post(self, post: Post, index: int):
        """Показать один пост с красивым форматированием"""
        # Заголовок поста
        author_text = Text(f"{post.author}", style="bold yellow")
        timestamp_text = Text(post.timestamp, style="dim")
        
        header = f"{index}. {author_text} {timestamp_text}"
        
        # Контент
        content = post.content
        if len(content) > 200:
            content = content[:197] + "..."
        
        # Статистика
        stats = f"💬 {post.replies} | ❤️ {post.likes}"
        
        # Собираем панель
        panel_content = f"""
{content}

[dim]{stats}[/dim]
"""
        
        panel = Panel(
            panel_content,
            title=header,
            border_style="blue",
            padding=(0, 1)
        )
        self.console.print(panel)
    
    def _get_command(self) -> str:
        """Получить команду от пользователя"""
        try:
            cmd = Prompt.ask(
                "[cyan]Команда[/cyan]",
                choices=["n", "p", "s", "r", "q"],
                show_choices=False
            ).lower().strip()
            return cmd
        except:
            return "q"
    
    def _handle_command(self, command: str) -> bool:
        """
        Обработать команду пользователя
        
        Returns:
            False если нужно выйти, True если продолжать
        """
        if command == "q":
            self.console.print("[yellow]⏹️  Спасибо за внимание![/yellow]")
            return False
            
        elif command == "n":
            # Следующая страница
            total_pages = (len(self.posts) + self.posts_per_page - 1) // self.posts_per_page
            if self.current_page < total_pages - 1:
                self.current_page += 1
            else:
                self.console.print("[yellow]⚠️  Вы в конце списка[/yellow]")
            return True
            
        elif command == "p":
            # Предыдущая страница
            if self.current_page > 0:
                self.current_page -= 1
            else:
                self.console.print("[yellow]⚠️  Вы в начале списка[/yellow]")
            return True
            
        elif command == "s":
            # Поиск
            query = Prompt.ask("[cyan]Введите поисковый запрос[/cyan]")
            if query:
                with self.console.status("[bold cyan]🔍 Ищем...", spinner="dots"):
                    try:
                        self.posts = self.api.search_posts(query, limit=50)
                        self.current_page = 0
                        if not self.posts:
                            self.console.print("[yellow]Ничего не найдено[/yellow]")
                        else:
                            self.console.print(f"[green]✓ Найдено {len(self.posts)} постов[/green]")
                    except Exception as e:
                        self.console.print(f"[red]Ошибка поиска: {e}[/red]")
            return True
            
        elif command == "r":
            # Перезагрузить
            self.posts = []
            self.current_page = 0
            return True
        
        return True
    
    def _retry_prompt(self) -> bool:
        """Спросить, повторить ли попытку"""
        retry = Prompt.ask(
            "[yellow]Повторить попытку?[/yellow]",
            choices=["y", "n"],
            default="y"
        ).lower()
        return retry == "y"
