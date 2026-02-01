import asyncio
from crawlee.crawlers import PlaywrightCrawler
from src.config import settings


async def main() -> None:
    """Инициализация и запуск PlaywrightCrawler."""
    crawler = PlaywrightCrawler(
        headless=settings.HEADLESS,
        browser_type="chromium",
    )

    @crawler.router.default_handler
    async def request_handler(context):
        """Обработчик по умолчанию."""
        await context.page.goto(settings.BASE_URL)
        title = await context.page.title()
        print(f"Page title: {title}")

    await crawler.run([settings.BASE_URL])


if __name__ == "__main__":
    asyncio.run(main())
