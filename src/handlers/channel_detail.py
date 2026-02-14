from crawlee.crawlers import PlaywrightCrawlingContext
from src.db.publication_dao import PublicationDAO
from src.handlers.max_parser_utils import parse_max_publication, create_publication_response
from src.handlers.svelte_selectors import (
    build_svelte_selector,
    query_selector_all_svelte
)

async def scroll_to_load(page, scrolls: int = 3) -> None:
    """Прокрутка страницы для подгрузки старых постов."""
    for _ in range(scrolls):
        await page.mouse.wheel(0, 2000)
        await page.wait_for_timeout(1000)

async def channel_detail_handler(context: PlaywrightCrawlingContext) -> None:
    """Обработчик для сбора детальной информации о канале MAX."""
    page = context.page
    # Извлекаем ID из URL (может быть /c/name или /-id)
    source_id = context.request.url.rstrip('/').split('/')[-1]
    dao = PublicationDAO()

    context.log.info(f"Processing channel: {source_id} (URL: {context.request.url})")
    
    # Ждем загрузки основного контента
    try:
        await page.wait_for_load_state('networkidle', timeout=15000)
    except:
        context.log.warning("Timeout waiting for networkidle, continuing...")
    
    # Проверяем наличие iframe webapp (в некоторых каналах контент может быть в нем)
    iframe_locator = page.locator('iframe[title="webapp"]')
    target = page
    if await iframe_locator.count() > 0:
        try:
            await iframe_locator.wait_for(state="visible", timeout=5000)
            target = iframe_locator.content_frame
            context.log.info("Parsing inside webapp iframe")
        except:
            context.log.info("Iframe not visible, parsing main page")

    await scroll_to_load(page)

    # Ждем появления сообщений (используем устойчивый селектор)
    bubble_selector = build_svelte_selector('bubble')
    try:
        await target.locator(bubble_selector).first.wait_for(timeout=10000)
    except Exception:
        context.log.warning(f"No messages found in channel {source_id} after waiting")
        # Попробуем сделать скриншот для отладки, если бы это был реальный краулер
        return

    posts_els = await query_selector_all_svelte(target, 'bubble')
    context.log.info(f"Found {len(posts_els)} posts in {source_id}")

    publications = []
    for el in posts_els:
        try:
            pub = await parse_max_publication(el, source_id)
            if pub and pub.content:
                await dao.save_publication(pub)
                publications.append(pub)
                # Логируем только каждый 5-й пост, чтобы не спамить
                if len(publications) % 5 == 0:
                    context.log.info(f"Saved {len(publications)} publications so far...")
        except Exception as e:
            context.log.error(f"Error parsing post in {source_id}: {e}")

    if publications:
        response = await create_publication_response(publications)
        context.log.info(
            f"COMPLETED {source_id}: {response.aggregations['stats']['total_count']} posts saved. "
            f"Total likes: {response.aggregations['stats']['total_likes']}"
        )
    else:
        context.log.warning(f"Finished {source_id} but 0 publications were parsed/saved")
