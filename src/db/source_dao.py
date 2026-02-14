"""DAO для работы с источниками (каналами) в SQLite."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from loguru import logger


@dataclass
class Source:
    """Модель источника (канала)."""

    name: str
    url: str
    category: str
    platform: str = "max"
    id: Optional[int] = None
    created_at: Optional[str] = None


class SourceDAO:
    """Data Access Object для источников."""

    def __init__(self, db_path: str | Path) -> None:
        """
        Инициализация DAO.

        Args:
            db_path: Путь к файлу БД
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_table()

    def _create_table(self) -> None:
        """Создает таблицу sources если не существует."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL UNIQUE,
                    category TEXT NOT NULL,
                    platform TEXT NOT NULL DEFAULT 'max',
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()
        logger.info(f"Таблица sources проверена/создана: {self.db_path}")

    def save(self, source: Source) -> bool:
        """
        Сохраняет источник в БД.

        Args:
            source: Объект источника

        Returns:
            True если сохранен, False если уже существует
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO sources (name, url, category, platform, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        source.name,
                        source.url,
                        source.category,
                        source.platform,
                        datetime.now().isoformat(),
                    ),
                )
                conn.commit()
                logger.debug(f"Источник сохранен: {source.name}")
                return True
            except sqlite3.IntegrityError:
                logger.debug(f"Источник уже существует: {source.name}")
                return False

    def count(self) -> int:
        """
        Возвращает количество источников в БД.

        Returns:
            Количество записей
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sources")
            result = cursor.fetchone()
            return result[0] if result else 0
