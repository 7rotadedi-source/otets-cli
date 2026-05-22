import sys
import argparse
from api.client import OtetsClient, OtetsAPIError
from ui.printer import print_post, print_error, print_help
from utils.config import get_limit

def main():
    parser = argparse.ArgumentParser(description="CLI клиент для ИТД")
    parser.add_argument('--limit', type=int, default=get_limit(), help='Количество постов')
    args = parser.parse_args()

    client = OtetsClient()
    current_page = 1
    limit = args.limit

    print(f"[bold green]Подключение к ИТД...[/bold green]")
    print_help()

    while True:
        try:
            posts = client.get_posts(page=current_page, limit=limit)
            
            if not posts:
                print_error("Посты не найдены.")
                break

            for post in posts:
                print_post(post)

            command = input("Команда (n/p/q): ").strip().lower()

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
