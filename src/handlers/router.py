from crawlee.crawlers import PlaywrightCrawlingContext
from crawlee.router import Router

# Я создаю роутер для распределения логики обработки страниц по разным обработчикам.

router = Router[PlaywrightCrawlingContext]()


@router.default_handler
async def default_handler(context: PlaywrightCrawlingContext) -> None:
    """Обработчик по умолчанию для всех страниц."""
    context.log.info(f"Processing {context.request.url}")


@router.handler("CHAT_DETAIL")
async def chat_detail_handler(context: PlaywrightCrawlingContext) -> None:
    """Обработчик страницы деталей чата."""
    context.log.info(f"Processing chat detail: {context.request.url}")
