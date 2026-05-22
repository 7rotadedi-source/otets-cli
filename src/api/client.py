import os
import requests
from dotenv import load_dotenv

load_dotenv()

class ItdSDKError(Exception):
    pass

class ItdUser:
    def __init__(self, username, base_url):
        self.username = username
        self.base_url = base_url
        self.session = requests.Session()
        
        # ВАЖНО: Вставь сюда реальное значение куки из браузера для теста
        # Или используй переменную окружения OTETS_COOKIE
        cookie_val = os.getenv('_ym_uid', '1778517092803469350')
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': f'{self.base_url}/@{self.username}',
        })
        
        if cookie_val:
            # Предполагаем, что кука называется access_token. Проверь название в браузере!
            self.session.cookies.set('access_token', cookie_val) 

    def get_posts(self, limit=20, sort='new'):
        url = f"{self.base_url}/api/posts/user/{self.username}"
        try:
            resp = self.session.get(url, params={'limit': limit, 'sort': sort}, timeout=10)
            
            # Если все еще 401, значит имя куки неверное или нужен Header Authorization
            if resp.status_code == 401:
                raise ItdSDKError("Ошибка 401: Требуется авторизация. Проверь OTETS_COOKIE в .env")
                
            resp.raise_for_status()
            data = resp.json()
            
            posts = data if isinstance(data, list) else data.get('data', [])
            return [self._normalize_post(p) for p in posts]
        except Exception as e:
            raise ItdSDKError(f"SDK Error: {e}")

    def _normalize_post(self, raw_post):
        import re
        from html import unescape
        
        content = raw_post.get('content', raw_post.get('body', raw_post.get('text', '')))
        if isinstance(content, str):
            content = re.sub('<[^<]+?>', '', unescape(content))
            
        return {
            'id': raw_post.get('id'),
            'title': raw_post.get('title', 'Без темы')[:60],
            'body': content[:1000],
            'link': f"{self.base_url}/@{self.username}/post/{raw_post.get('id')}",
            'date': raw_post.get('createdAt', '')
        }

class ItdPlatform:
    def __init__(self, base_url=None, username=None):
        self.base_url = base_url or os.getenv('OTETS_BASE_URL', 'https://xn--d1ah4a.com')
        self.username = username or os.getenv('OTETS_USERNAME', 'fau1t')
    
    def get_user(self):
        return ItdUser(self.username, self.base_url)
