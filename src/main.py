import asyncio
from crawlee.crawlers import PlaywrightCrawler
from src.config import settings
from src.handlers.router import router


async def main() -> None:
    """Инициализация и запуск PlaywrightCrawler."""
    crawler = PlaywrightCrawler(
        request_handler=router,
        headless=True, # Включаем headless=False для отладки, чтобы видеть что происходит
        browser_type="chromium",
        user_data_dir=settings.USER_DATA_DIR,
        max_requests_per_crawl=50,
    )

    # Запускаем с базового URL
    await crawler.run([settings.BASE_URL])


if __name__ == "__main__":
    asyncio.run(main())
