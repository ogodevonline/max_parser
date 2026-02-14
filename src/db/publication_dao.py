import sqlite3
import json
from src.models.publication import Publication

class PublicationDAO:
    """
    DAO для работы с публикациями в SQLite.
    Инкапсулирует создание таблиц и транзакции.
    """
    def __init__(self, db_path: str = "storage/publications.db") -> None:
        self.db_path = db_path
        self._create_table()

    def _create_table(self) -> None:
        """Создает таблицу публикаций с поддержкой всех полей модели."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS publications (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    content TEXT,
                    source_id TEXT,
                    source_type TEXT,
                    published_ts INTEGER,
                    url TEXT,
                    views INTEGER,
                    likes INTEGER,
                    reposts INTEGER,
                    comments INTEGER,
                    media TEXT,
                    forward_from TEXT,
                    location TEXT,
                    related_resources TEXT,
                    language TEXT,
                    sentiment TEXT,
                    topics TEXT,
                    entities TEXT
                )
            """)

    async def save_publication(self, pub: Publication) -> None:
        """Сохраняет публикацию, используя INSERT OR REPLACE."""
        data = pub.model_dump()
        # Сериализуем сложные типы в JSON для хранения в SQLite
        for key in ['media', 'location', 'related_resources', 'topics', 'entities']:
            if data[key] is not None:
                data[key] = json.dumps(data[key])
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO publications (
                    id, title, content, source_id, source_type, published_ts,
                    url, views, likes, reposts, comments, media, forward_from,
                    location, related_resources, language, sentiment, topics, entities
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['id'], data['title'], data['content'], data['source_id'],
                data['source_type'], data['published_ts'], data['url'],
                data['views'], data['likes'], data['reposts'], data['comments'],
                data['media'], data['forward_from'], data['location'],
                data['related_resources'], data['language'], data['sentiment'],
                data['topics'], data['entities']
            ))
