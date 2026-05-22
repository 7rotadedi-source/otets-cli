"""
API клиент для взаимодействия с ИТД
"""

import requests
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from utils.errors import OtetsError, NetworkError


@dataclass
class Post:
    """Модель поста"""
    id: str
    author: str
    content: str
    timestamp: str
    likes: int = 0
    replies: int = 0
    
    def __str__(self) -> str:
        return f"Post(id={self.id}, author={self.author}, likes={self.likes})"


class OtetsAPI:
    """Клиент для работы с API ИТД"""
    
    def __init__(self, base_url: str = "https://xn--d1ah4a.com", username: str = ""):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "OtetsTerminalClient/1.0"
        })
        self._cache: Dict[str, Any] = {}
        
    def get_profile_posts(
        self, 
        username: Optional[str] = None, 
        limit: int = 10,
        offset: int = 0
    ) -> List[Post]:
        """
        Получить посты пользователя
        
        Args:
            username: Имя пользователя (если None, используется username из конфига)
            limit: Максимум постов
            offset: Смещение для пагинации
            
        Returns:
            Список постов
            
        Raises:
            NetworkError: Ошибка сети
            OtetsError: Ошибка API
        """
        if not username:
            username = self.username
            
        try:
            # Пример: получаем посты с публичного API или парсим HTML
            # Здесь можно использовать разные эндпоинты в зависимости от API ИТД
            
            url = f"{self.base_url}/api/posts"
            params = {
                "author": username,
                "limit": limit,
                "offset": offset
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            posts = self._parse_posts(data.get("posts", []))
            
            return posts
            
        except requests.exceptions.Timeout:
            raise NetworkError("Timeout: сервер не ответил за 10 секунд")
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Ошибка соединения: {e}")
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                raise OtetsError(f"Пользователь '{username}' не найден")
            raise OtetsError(f"HTTP {response.status_code}: {e}")
        except Exception as e:
            raise OtetsError(f"Ошибка при получении постов: {e}")
    
    def search_posts(self, query: str, limit: int = 10) -> List[Post]:
        """
        Поиск постов по ключевым словам
        
        Args:
            query: Поисковый запрос
            limit: Максимум результатов
            
        Returns:
            Список найденных постов
        """
        try:
            url = f"{self.base_url}/api/search"
            params = {
                "q": query,
                "limit": limit,
                "type": "posts"
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            posts = self._parse_posts(data.get("results", []))
            
            return posts
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Ошибка при поиске: {e}")
    
    def get_post_replies(self, post_id: str) -> List[Post]:
        """Получить ответы на пост"""
        try:
            url = f"{self.base_url}/api/posts/{post_id}/replies"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            posts = self._parse_posts(data.get("replies", []))
            
            return posts
            
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Ошибка при получении ответов: {e}")
    
    @staticmethod
    def _parse_posts(data: List[Dict[str, Any]]) -> List[Post]:
        """Преобразовать JSON в объекты Post"""
        posts = []
        
        for item in data:
            try:
                post = Post(
                    id=str(item.get("id", "")),
                    author=item.get("author", "Unknown"),
                    content=item.get("content", ""),
                    timestamp=item.get("timestamp", ""),
                    likes=item.get("likes", 0),
                    replies=item.get("replies", 0)
                )
                posts.append(post)
            except Exception:
                # Пропускаем некорректные посты
                continue
        
        return posts
    
    def close(self):
        """Закрыть сессию"""
        self.session.close()
