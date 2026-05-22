import os
import requests
from dotenv import load_dotenv

load_dotenv()

class OtetsAPIError(Exception):
    pass

class OtetsClient:
    def __init__(self):
        self.base_url = os.getenv('OTETS_BASE_URL', 'https://xn--d1ah4a.com')
        self.username = os.getenv('OTETS_USERNAME', 'fau1t')
        self.session = requests.Session()
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': f'{self.base_url}/@{self.username}',
        })

    def get_posts(self, page=1, limit=20):
        url = f"{self.base_url}/api/posts/user/{self.username}"
        
        params = {
            'limit': limit,
            'sort': 'new',
        }

        try:
            response = self.session.get(url, params=params, timeout=10)
            
            # Обработка ошибки 401 (Unauthorized)
            if response.status_code == 401:
                raise OtetsAPIError("Ошибка 401: Требуется авторизация. Проверьте токен или куки.")
            
            response.raise_for_status()
            data = response.json()
            
            posts_list = []
            if isinstance(data, list):
                posts_list = data
            elif isinstance(data, dict) and 'data' in data:
                posts_list = data['data']
            else:
                posts_list = [data] if data else []

            formatted_posts = []
            for p in posts_list:
                post_id = p.get('id', 'unknown')
                title = p.get('title', 'Без заголовка')
                content = p.get('content', p.get('body', p.get('text', '')))
                
                # Очистка от HTML тегов
                clean_content = content
                if isinstance(content, str) and '<' in content:
                    from html import unescape
                    import re
                    clean_content = re.sub('<[^<]+?>', '', unescape(content))

                formatted_posts.append({
                    'id': post_id,
                    'title': title[:60] if title else f"Пост #{str(post_id)[:8]}",
                    'body': clean_content[:1000],
                    'link': f"{self.base_url}/@{self.username}/post/{post_id}",
                    'created_at': p.get('createdAt', p.get('created_at', ''))
                })
                
            return formatted_posts

        except requests.exceptions.HTTPError as e:
            raise OtetsAPIError(f"Ошибка API: {e}")
        except Exception as e:
            raise OtetsAPIError(f"Ошибка соединения: {e}")

    def search_posts(self, query):
        return []
