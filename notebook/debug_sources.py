"""
Отладочный скрипт для парсинга источников (каналов) MAX платформы.

Использует playwright + bs4 для парсинга.
Навигация: Поиск → Каналы → Выбор категории → Сбор всех источников
Результаты сохраняются в SQLite: storage/sources.db
"""

import asyncio
import os
import sys
from pathlib import Path

from loguru import logger
from playwright.async_api import async_playwright

# Добавляем корень проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config import settings
from src.db.source_dao import SourceDAO
from src.handlers.source_parser import SourceParser


async def run_debug_sources() -> None:
    """Основная функция парсинга источников."""
    logger.info(">>> Запуск парсинга источников...")

    # Инициализация DAO
    storage_dir = Path(__file__).parent.parent / "storage"
    db_path = storage_dir / "sources.db"
    dao = SourceDAO(db_path)

    # Инициализация парсера
    parser = SourceParser(dao)

    async with async_playwright() as p:
        # Инициализация браузера с сохранением сессии
        context = await p.chromium.launch_persistent_context(
            user_data_dir=settings.USER_DATA_DIR,
            headless=settings.HEADLESS,
            viewport={
                "width": settings.VIEWPORT_WIDTH,
                "height": settings.VIEWPORT_HEIGHT,
            },
        )

        try:
            # Парсинг всех источников
            total_saved, total_count = await parser.parse_all_sources(context)

            # Итоговая статистика
            logger.info(
                f"\n>>> ИТОГ: сохранено новых {total_saved}, всего в БД: {total_count}"
            )
        finally:
            await context.close()


if __name__ == "__main__":
    asyncio.run(run_debug_sources())
