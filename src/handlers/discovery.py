from crawlee.crawlers import PlaywrightCrawlingContext
from src.db.publication_dao import PublicationDAO
from src.handlers.max_parser_utils import parse_max_publication
from src.handlers.svelte_selectors import query_selector_all_svelte


async def discovery_handler(context: PlaywrightCrawlingContext) -> None:
    """Обработчик для поиска и парсинга каналов (логика из debug_max_v2)."""
    page = context.page
    context.log.info(f"Starting discovery on {context.request.url}")

    # 1. Навигация к поиску и каналам
    await page.get_by_role("textbox", name="Поиск").click()
    await page.get_by_role("button", name="Каналы").click()
    
    iframe_locator = page.locator('iframe[title="webapp"]')
    await iframe_locator.wait_for(state="visible", timeout=15000)
    iframe = iframe_locator.content_frame
    context.log.info("Iframe webapp found")

    # 2. Выбор категории
    category = iframe.get_by_text("Новости и политика").first
    await category.wait_for(state="visible")
    await category.click()
    context.log.info("Category selected")
    
    # Ждем появления кнопок каналов (важно!)
    await iframe.get_by_role("button").first.wait_for(state="visible", timeout=10000)
    await page.wait_for_timeout(2000)

    # 3. Сбор и парсинг каналов
    dao = PublicationDAO()

    # Получаем все кнопки
    channel_buttons = await iframe.get_by_role("button").all()
    context.log.info(f"Found {len(channel_buttons)} buttons in iframe")

    # Проходим по кнопкам (начиная со второй, как в debug_max_v2)
    for i in range(1, min(6, len(channel_buttons))):
        try:
            # Пересобираем кнопки на каждой итерации, чтобы избежать stale elements
            current_buttons = await iframe.get_by_role("button").all()
            if i >= len(current_buttons):
                break
                
            btn = current_buttons[i]
            source_id = await btn.get_attribute("name") or f"channel_{i}"
            context.log.info(f"Opening channel: {source_id}")
            
            await btn.click()
            await page.wait_for_timeout(3000)

            # Парсинг публикаций (используем устойчивый селектор)
            posts_els = await query_selector_all_svelte(page, 'bubble')
            if not posts_els:
                posts_els = await query_selector_all_svelte(iframe, 'bubble')
            
            context.log.info(f"Found {len(posts_els)} posts in {source_id}")
            
            publications = []
            for el in posts_els[:10]:
                pub = await parse_max_publication(el, source_id)
                if pub:
                    await dao.save_publication(pub)
                    publications.append(pub)
            
            if publications:
                context.log.info(f"Saved {len(publications)} posts for {source_id}")

            # Возвращаемся к списку каналов
            await page.go_back()
            await iframe_locator.wait_for(state="visible", timeout=15000)
            # Ждем прогрузки списка после возврата
            await iframe.get_by_role("button").first.wait_for(state="visible")
            await page.wait_for_timeout(1000)

        except Exception as e:
            context.log.error(f"Error processing channel at index {i}: {e}")
            # Попытка восстановления
            await page.goto(context.request.url)
            await page.get_by_role("textbox", name="Поиск").click()
            await page.get_by_role("button", name="Каналы").click()
            await iframe_locator.wait_for(state="visible")
            category = iframe.get_by_text("Новости и политика").first
            await category.click()
            await page.wait_for_timeout(2000)
