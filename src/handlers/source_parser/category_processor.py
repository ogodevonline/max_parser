"""Обработка категорий и каналов."""

import asyncio

from loguru import logger
from playwright.async_api import Frame, Page

from src.db.source_dao import Source, SourceDAO
from src.handlers.source_parser.navigator import BrowserNavigator


class CategoryProcessor:
    """Обработка категорий и извлечение каналов."""

    def __init__(self, dao: SourceDAO, navigator: BrowserNavigator) -> None:
        """
        Инициализация процессора.

        Args:
            dao: DAO для сохранения источников
            navigator: Навигатор для работы с iframe
        """
        self.dao = dao
        self.navigator = navigator

    async def parse_channels_in_category(
        self, iframe: Frame, category_name: str
    ) -> int:
        """
        Парсит каналы внутри категории.

        Args:
            iframe: Frame с каналами
            category_name: Название категории

        Returns:
            Количество сохраненных каналов
        """
        channel_cells = await iframe.locator(
            'label [class*="CellSimple"][role="button"]'
        ).all()
        logger.info(f"Найдено каналов в '{category_name}': {len(channel_cells)}")

        saved_count = 0
        for channel_cell in channel_cells:
            try:
                title_el = channel_cell.locator('[class*="CellSimple__title"]')
                channel_name = await title_el.inner_text()
                channel_name = channel_name.strip()

                channel_url = f"https://web.max.ru/channel/{channel_name}"

                source = Source(
                    name=channel_name, url=channel_url, category=category_name
                )
                if self.dao.save(source):
                    saved_count += 1
                    logger.debug(f"Сохранен: {channel_name}")

            except Exception as e:
                logger.error(f"Ошибка парсинга канала: {e}")
                continue

        return saved_count

    async def process_category(self, page: Page, category_name: str) -> int:
        """
        Обрабатывает одну категорию.

        Поток:
        1. Клик на категорию по имени
        2. Проверка, что это категория (есть кнопка "Назад")
        3. Парсинг каналов
        4. Возврат назад

        Args:
            page: Страница браузера
            category_name: Название категории

        Returns:
            Количество сохраненных каналов
        """
        logger.info(f"\n>>> Обработка категории: {category_name}")

        # Кликаем на категорию по имени
        iframe = await self.navigator.get_iframe(page)
        category_btn = iframe.get_by_role("button", name=category_name)
        await category_btn.click()
        await asyncio.sleep(2.5)

        # Проверяем, что открылась категория (есть кнопка "Назад")
        try:
            await page.get_by_label("Назад").wait_for(state="visible", timeout=5000)
        except Exception as e:
            logger.warning(f"'{category_name}' не является категорией: {e}")
            await self.navigator.go_back(page)
            return 0

        # Скроллим для загрузки всех каналов
        iframe = await self.navigator.get_iframe(page)
        await self.navigator.scroll_iframe(iframe)

        # Парсим каналы
        iframe = await self.navigator.get_iframe(page)
        saved = await self.parse_channels_in_category(iframe, category_name)

        # Возвращаемся назад
        await self.navigator.go_back(page)

        logger.info(f"Категория '{category_name}': сохранено {saved} каналов")
        return saved
