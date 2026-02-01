from crawlee.crawlers import PlaywrightCrawlingContext
from crawlee.router import Router
from src.handlers.discovery import discovery_handler

# Я подключаю discovery_handler к роутеру для обработки начальной страницы.

router = Router[PlaywrightCrawlingContext]()


@router.default_handler
async def default_handler(context: PlaywrightCrawlingContext) -> None:
    """Обработчик по умолчанию для всех страниц."""
    await discovery_handler(context)


@router.handler("CHAT_DETAIL")
async def chat_detail_handler(context: PlaywrightCrawlingContext) -> None:
    """Обработчик страницы деталей чата."""
    context.log.info(f"Processing chat detail: {context.request.url}")
