from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text

console = Console()

def print_post(post):
    title = Text(post.get('title', 'Без названия'), style="bold cyan")
    body = post.get('body', '')
    
    try:
        content = Markdown(body)
    except:
        content = body

    panel = Panel(
        content,
        title=title,
        border_style="blue",
        padding=(1, 2)
    )
    console.print(panel)
    console.print()

def print_error(message):
    console.print(f"[bold red]Ошибка:[/bold red] {message}")

def print_help():
    help_text = """
[n]ext - следующий пост
[p]rev - предыдущий пост
[q]uit - выход
    """
    console.print(Panel(help_text, title="Помощь", border_style="yellow"))
