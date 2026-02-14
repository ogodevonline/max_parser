"""Навигация по MAX платформе."""

import asyncio
import re

from loguru import logger
from playwright.async_api import Frame, Page


class BrowserNavigator:
    """Навигация по браузеру и iframe."""

    async def get_iframe(self, page: Page) -> Frame:
        """
        Получает iframe webapp.

        Args:
            page: Страница браузера

        Returns:
            Frame объект iframe
        """
        iframe_locator = page.locator('iframe[title="webapp"]')
        await iframe_locator.wait_for(state="attached", timeout=10000)

        iframe_element = await iframe_locator.element_handle()
        if iframe_element is None:
            raise RuntimeError("Не удалось получить ElementHandle из iframe")

        iframe = await iframe_element.content_frame()
        if iframe is None:
            raise RuntimeError("Не удалось получить content_frame из iframe")

        return iframe

    async def navigate_to_channels(self, page: Page) -> None:
        """
        Навигация: Поиск → Каналы.

        Args:
            page: Страница браузера
        """
        logger.info("Навигация: Поиск → Каналы")
        await page.get_by_placeholder("Поиск").click()
        await asyncio.sleep(0.5)
        await page.get_by_role("button", name="Каналы", exact=True).click()
        await asyncio.sleep(2)

    async def expand_topics(self, iframe: Frame) -> None:
        """
        Кликает 'Показать ещё' в разделе 'Темы'.

        Args:
            iframe: Frame с каналами
        """
        logger.info("Поиск кнопки 'Показать ещё' в разделе 'Темы'")

        try:
            # Используем regex для точного поиска раздела "Темы"
            topics_section = iframe.locator("div").filter(
                has_text=re.compile(r"^ТемыПоказать ещё$")
            )
            show_more_btn = topics_section.get_by_role("button")
            await show_more_btn.click()
            await asyncio.sleep(1)
            logger.info("Кнопка 'Показать ещё' нажата")
        except Exception as e:
            logger.warning(f"Кнопка 'Показать ещё' не найдена: {e}")

    async def scroll_iframe(self, iframe: Frame, iterations: int = 30) -> None:
        """
        Скроллинг iframe для загрузки всех элементов.

        Args:
            iframe: Frame для скролла
            iterations: Количество итераций скролла
        """
        logger.debug(f"Скроллинг iframe ({iterations} итераций)...")
        for i in range(iterations):
            await iframe.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(0.5)

    async def go_back(self, page: Page) -> None:
        """
        Возврат назад через кнопку "Назад".

        Args:
            page: Страница браузера
        """
        try:
            await page.get_by_label("Назад").click()
            await asyncio.sleep(1.5)
        except Exception as e:
            logger.warning(f"Не удалось вернуться назад: {e}")

    async def get_topics_categories(self, iframe: Frame) -> list[str]:
        """
        Получает список категорий из раздела "Темы".

        Args:
            iframe: Frame с каналами

        Returns:
            Список названий категорий
        """
        # Находим раздел "Темы" и получаем все кнопки внутри него
        topics_section = (
            iframe.locator("div").filter(has_text=re.compile(r"^Темы")).first
        )

        # Получаем все кнопки внутри раздела "Темы"
        # Категории имеют role="button" и находятся в CellSimple
        category_buttons = await topics_section.locator(
            '[class*="CellSimple"][role="button"]'
        ).all()

        categories = []
        for button in category_buttons:
            try:
                # Получаем текст из title элемента
                title_el = button.locator('[class*="CellSimple__title"]')
                text = await title_el.inner_text()
                text = text.strip()

                if text:
                    categories.append(text)

            except Exception as e:
                logger.debug(f"Ошибка чтения категории: {e}")
                continue

        logger.info(f"Найдено категорий в 'Темы': {len(categories)}")
        return categories
