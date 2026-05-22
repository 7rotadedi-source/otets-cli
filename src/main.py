import sys
from api.client import OtetsClient, OtetsAPIError
from ui.printer import print_post, print_error, print_help
from utils.config import get_limit

def main():
    # Инициализация клиента
    try:
        client = OtetsClient()
    except Exception as e:
        print_error(f"Ошибка инициализации: {e}")
        return

    limit = get_limit()
    current_page = 1

    print(f"[bold green]Otets CLI v1.0[/bold green]")
    print_help()

    while True:
        try:
            # Получаем посты через API клиент
            posts = client.get_posts(page=current_page, limit=limit)
            
            if not posts:
                print_error("Лента пуста или нет доступа.")
                break

            for post in posts:
                print_post(post)

            command = input("\nКоманда (n/p/q): ").strip().lower()

            if command == 'q':
                print("Выход...")
                break
            elif command == 'n':
                current_page += 1
            elif command == 'p':
                if current_page > 1:
                    current_page -= 1
                else:
                    print_error("Это первая страница.")
            else:
                print_error("Неизвестная команда.")

        except OtetsAPIError as e:
            print_error(str(e))
            break
        except KeyboardInterrupt:
            print("\nВыход...")
            break
        except EOFError:
            break

if __name__ == '__main__':
    main()
