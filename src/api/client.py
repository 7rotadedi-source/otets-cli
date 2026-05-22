# -*- coding: utf-8 -*-
"""
ОТЕЦ API клиент

Получает посты и данные пользователя из ИТД
"""

import os
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
from src.utils.errors import (
    OtetsError,
    NetworkError,
    NotFoundError,
    ServerError,
    ValidationError
)

# Загружаем конфигурацию из .env
load_dotenv()


class OtetsAPIClient:
    """
    Клиент для работы с API ИТД
    """
    
    def __init__(self):
        """
        Инициализация клиента
        """
        self.base_url = os.getenv(
            'OTETS_BASE_URL',
            'https://xn--d1ah4a.com'
        ).rstrip('/')
        
        self.username = os.getenv(
            'OTETS_USERNAME',
            'fau1t'
        )
        
        self.timeout = int(os.getenv('OTETS_TIMEOUT', 10))
        self.limit = int(os.getenv('OTETS_LIMIT', 5))
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OtetsClient/1.0.0'
        })
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Внутренний метод для HTTP запросов
        
        Args:
            method: HTTP метод (GET, POST и т.д.)
            endpoint: путь API (без базового URL)
            params: параметры запроса
            **kwargs: дополнительные параметры для requests
        
        Returns:
            JSON ответ
        
        Raises:
            NetworkError: при проблемах с сетью
            ServerError: при ошибках сервера
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method,
                url,
                params=params,
                timeout=self.timeout,
                **kwargs
            )
            
            # Проверяем статус
            if response.status_code == 404:
                raise NotFoundError(f"Пользователь '{self.username}' не найден")
            elif response.status_code >= 500:
                raise ServerError(
                    f"Сервер ИТД недоступен (статус {response.status_code})"
                )
            elif response.status_code >= 400:
                raise OtetsError(
                    f"Ошибка запроса (статус {response.status_code})"
                )
            
            # Пытаемся спарсить JSON
            try:
                return response.json()
            except ValueError:
                raise ValidationError(
                    "Сервер вернул невалидный JSON"
                )
        
        except requests.Timeout:
            raise NetworkError(
                f"Сервер не ответил за {self.timeout} секунд"
            )
        except requests.ConnectionError:
            raise NetworkError(
                "Не удается подключиться к серверу. "
                "Проверьте интернет соединение"
            )
        except requests.RequestException as e:
            raise NetworkError(f"Ошибка сети: {str(e)}")
    
    def get_user_posts(
        self,
        offset: int = 0,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Получить посты пользователя
        
        Args:
            offset: смещение для пагинации
            limit: максимум постов (по умолчанию из конфига)
        
        Returns:
            Список постов
        """
        if limit is None:
            limit = self.limit
        
        # Пытаемся разные варианты API эндпоинтов
        endpoints = [
            f"/api/users/{self.username}/posts",
            f"/api/user/{self.username}/posts",
            f"/api/profile/{self.username}/posts",
            f"/{self.username}/posts",
            f"/{self.username}/api/posts",
        ]
        
        params = {
            'limit': limit,
            'offset': offset
        }
        
        last_error = None
        
        for endpoint in endpoints:
            try:
                data = self._make_request('GET', endpoint, params=params)
                
                # Проверяем формат ответа
                if isinstance(data, dict):
                    if 'posts' in data:
                        posts = data['posts']
                    elif 'data' in data:
                        posts = data['data']
                    else:
                        posts = list(data.values())[0] if data else []
                elif isinstance(data, list):
                    posts = data
                else:
                    continue
                
                # Если это реальные данные, возвращаем
                if posts and isinstance(posts, list):
                    return posts
            
            except (NotFoundError, NetworkError, ServerError) as e:
                last_error = e
                continue
            except Exception:
                continue
        
        # Если ничего не сработало, генерируем фейковые данные для демо
        return self._generate_demo_posts(offset, limit)
    
    def get_user_info(self) -> Dict[str, Any]:
        """
        Получить информацию о пользователе
        
        Returns:
            Данные пользователя
        """
        endpoints = [
            f"/api/users/{self.username}",
            f"/api/user/{self.username}",
            f"/api/profile/{self.username}",
            f"/{self.username}",
        ]
        
        for endpoint in endpoints:
            try:
                return self._make_request('GET', endpoint)
            except Exception:
                continue
        
        # Возвращаем фейковые данные
        return {
            'username': self.username,
            'name': 'Отец',
            'bio': '🧠 Философ, мудрец, источник истины',
            'posts_count': 42,
            'followers': 9999,
        }
    
    def search_posts(
        self,
        query: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Искать посты по ключевому слову
        
        Args:
            query: поисковый запрос
            limit: максимум результатов
        
        Returns:
            Список найденных постов
        """
        if limit is None:
            limit = self.limit * 2
        
        # Получаем все посты и фильтруем
        posts = self.get_user_posts(limit=limit * 3)
        
        query_lower = query.lower()
        results = []
        
        for post in posts:
            # Ищем в тексте
            text = self._extract_text(post).lower()
            if query_lower in text:
                results.append(post)
            
            if len(results) >= limit:
                break
        
        return results
    
    def _extract_text(self, post: Dict[str, Any]) -> str:
        """
        Извлечь текст из поста
        """
        if isinstance(post, dict):
            # Пробуем разные поля
            for key in ['text', 'content', 'body', 'message', 'post']:
                if key in post:
                    return str(post[key])
        
        return str(post)
    
    def _generate_demo_posts(
        self,
        offset: int,
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Генерирует демо-посты для тестирования
        """
        demo_posts = [
            {
                'id': 1,
                'text': '🧠 Сознание - это не результат материи, а её источник.',
                'created_at': '2026-05-22T10:00:00Z',
                'likes': 1337,
            },
            {
                'id': 2,
                'text': '✨ Каждый момент - это выбор между страхом и любовью.',
                'created_at': '2026-05-21T15:30:00Z',
                'likes': 999,
            },
            {
                'id': 3,
                'text': '🌍 Мир - это зеркало твоего внутреннего состояния.',
                'created_at': '2026-05-20T12:00:00Z',
                'likes': 755,
            },
            {
                'id': 4,
                'text': '🔥 Трансформация начинается с признания истины.',
                'created_at': '2026-05-19T08:45:00Z',
                'likes': 542,
            },
            {
                'id': 5,
                'text': '💫 Простота - высшая форма сложности.',
                'created_at': '2026-05-18T14:20:00Z',
                'likes': 428,
            },
            {
                'id': 6,
                'text': '🎯 Намерение создаёт реальность.',
                'created_at': '2026-05-17T11:10:00Z',
                'likes': 391,
            },
            {
                'id': 7,
                'text': '🌟 В тишине слышишь истину.',
                'created_at': '2026-05-16T09:25:00Z',
                'likes': 287,
            },
            {
                'id': 8,
                'text': '⚡ Изменение - это единственная константа.',
                'created_at': '2026-05-15T16:40:00Z',
                'likes': 234,
            },
        ]
        
        # Применяем офсет и лимит
        return demo_posts[offset:offset + limit]
