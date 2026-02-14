"""Извлечение данных из HTML элементов."""

from typing import Optional

from bs4 import BeautifulSoup
from loguru import logger

from src.db.source_dao import Source


class DataExtractor:
    """Извлечение данных источников из HTML."""

    async def parse_source_from_element(
        self, element, category: str
    ) -> Optional[Source]:
        """
        Парсит источник из HTML элемента.

        Args:
            element: Playwright element (Locator)
            category: Категория источника

        Returns:
            Source или None если не удалось распарсить
        """
        try:
            name_attr = await element.get_attribute("name")
            name: str | None = None

            if name_attr and isinstance(name_attr, str):
                name = name_attr
            else:
                html = await element.inner_html()
                soup = BeautifulSoup(html, "html.parser")

                button = soup.find("button")
                if button:
                    button_name = button.get("name")
                    if button_name and isinstance(button_name, str):
                        name = button_name
                    else:
                        name = button.get_text(strip=True)

                if not name:
                    text_elements = soup.find_all(string=True)
                    for text in text_elements:
                        if text.strip():
                            name = text.strip()
                            break

            if not name:
                return None

            url = f"https://web.max.ru/channel/{name}"
            return Source(name=name, url=url, category=category)

        except Exception as e:
            logger.error(f"Ошибка парсинга элемента: {e}")
            return None
