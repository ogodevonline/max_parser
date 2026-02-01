import asyncio
import random
from crawlee.crawlers import PlaywrightCrawlingContext


async def discovery_handler(context: PlaywrightCrawlingContext) -> None:
    """Обработчик для поиска и сбора ссылок на чаты."""
    context.log.info(f"Starting discovery on {context.request.url}")
    
    # Ожидание появления списка чатов
    selector = '.channel-item-link'
    await context.page.wait_for_selector(selector, timeout=30000)
    
    # Сбор первых 10 ссылок
    links = await context.page.locator(selector).evaluate_all(
        '(elements) => elements.slice(0, 10).map(el => el.href)'
    )
    
    context.log.info(f"Found {len(links)} chat links")
    
    for link in links:
        # Имитация человека: случайная задержка 1-3 сек
        delay = random.uniform(1, 3)
        await asyncio.sleep(delay)
        
        # Добавление ссылки в очередь с меткой CHAT_DETAIL
        await context.enqueue_links(
            selector=f'a[href="{link}"]',
            label='CHAT_DETAIL',
        )
        context.log.info(f"Enqueued chat detail: {link} (after {delay:.2f}s delay)")
