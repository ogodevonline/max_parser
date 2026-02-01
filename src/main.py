import asyncio
from crawlee.crawlers import PlaywrightCrawler
from src.config import settings
from src.handlers.router import router


async def main() -> None:
    """Инициализация и запуск PlaywrightCrawler."""
    crawler = PlaywrightCrawler(
        request_handler=router,
        headless=settings.HEADLESS,
        browser_type="chromium",
        # Crawlee использует PlaywrightBrowserContextOptions для настройки
    )

    await crawler.run([settings.BASE_URL])


if __name__ == "__main__":
    asyncio.run(main())
