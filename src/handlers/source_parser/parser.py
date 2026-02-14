"""Основная логика парсинга источников."""

import asyncio

from loguru import logger
from playwright.async_api import BrowserContext, Page

from src.config import settings
from src.db.source_dao import SourceDAO
from src.handlers.source_parser.category_processor import CategoryProcessor
from src.handlers.source_parser.navigator import BrowserNavigator


class SourceParser:
    """Парсер для извлечения источников с MAX платформы."""

    def __init__(self, dao: SourceDAO) -> None:
        """
        Инициализация парсера.

        Args:
            dao: DAO для сохранения источников
        """
        self.dao = dao
        self.navigator = BrowserNavigator()
        self.processor = CategoryProcessor(dao, self.navigator)

    async def _init_page(self, page: Page) -> None:
        """
        Инициализирует страницу и навигацию.

        Поток:
        1. Открыть https://web.max.ru/
        2. Клик "Поиск"
        3. Клик "Каналы"
        4. Клик "Показать ещё" в "Темы"

        Args:
            page: Страница браузера
        """
        await page.goto(settings.BASE_URL)
        logger.info(f"Открыта страница: {page.url}")
        await asyncio.sleep(3)

        await self.navigator.navigate_to_channels(page)

        iframe = await self.navigator.get_iframe(page)
        await self.navigator.expand_topics(iframe)

    async def _parse_categories(self, page: Page) -> int:
        """
        Парсит все категории из раздела "Темы".

        Args:
            page: Страница браузера

        Returns:
            Количество сохраненных каналов
        """
        iframe = await self.navigator.get_iframe(page)
        categories = await self.navigator.get_topics_categories(iframe)

        if not categories:
            logger.error("Категории в разделе 'Темы' не найдены")
            return 0

        total_saved = 0
        processed = set()

        for category_name in categories:
            if category_name in processed:
                continue

            processed.add(category_name)

            try:
                saved = await self.processor.process_category(page, category_name)
                total_saved += saved
            except Exception as e:
                logger.error(f"Ошибка обработки '{category_name}': {e}")
                continue

        return total_saved

    async def parse_all_sources(self, context: BrowserContext) -> tuple[int, int]:
        """
        Парсит все источники из MAX.

        Новый поток:
        1. Открыть https://web.max.ru/
        2. Клик "Поиск" → "Каналы"
        3. Клик "Показать ещё" в "Темы"
        4. Итерация по категориям: клик → парсинг → назад

        Args:
            context: Контекст браузера

        Returns:
            Кортеж (новых_сохранено, всего_в_БД)
        """
        page = await context.new_page()

        await self._init_page(page)
        total_saved = await self._parse_categories(page)

        total_count = self.dao.count()
        return total_saved, total_count
