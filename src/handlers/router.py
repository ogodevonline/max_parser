from crawlee.crawlers import PlaywrightCrawlingContext
from src.handlers.discovery import discovery_handler
from src.handlers.channel_detail import channel_detail_handler
from crawlee.router import Router

router = Router[PlaywrightCrawlingContext]()

@router.default_handler
async def default_handler(context: PlaywrightCrawlingContext) -> None:
    """Обработчик по умолчанию."""
    await discovery_handler(context)

@router.handler("CHAT_DETAIL")
async def chat_detail_route(context: PlaywrightCrawlingContext) -> None:
    """Маршрут для деталей (если понадобится в будущем)."""
    await channel_detail_handler(context)
