import os
import sys
import asyncio
import time
from playwright.async_api import async_playwright

# Добавляем корень проекта в sys.path для импорта модулей
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import settings
from src.models.publication import Publication, PublicationResponse
from src.handlers.svelte_selectors import (
    query_selector_svelte,
    query_selector_all_svelte
)

async def step_1_init():
    """Шаг 1: Инициализация браузера и проверка авторизации."""
    print("\n>>> Шаг 1: Инициализация браузера...")
    p = await async_playwright().start()
    context = await p.chromium.launch_persistent_context(
        user_data_dir=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', settings.USER_DATA_DIR)),
        headless=False,
        viewport={'width': 1280, 'height': 720}
    )
    page = await context.new_page()
    await page.goto(settings.BASE_URL)
    print(f"Открыта страница: {page.url}")
    return p, context, page

async def step_2_navigate(page):
    """Шаг 2: Поиск и переход к списку каналов."""
    print("\n>>> Шаг 2: Переход к списку каналов...")
    await page.get_by_role("textbox", name="Поиск").click()
    await page.get_by_role("button", name="Каналы").click()
    iframe_locator = page.locator('iframe[title="webapp"]')
    await iframe_locator.wait_for(state="visible", timeout=15000)
    iframe = iframe_locator.content_frame
    print("Iframe webapp найден")
    return iframe

async def step_3_list_channels(iframe):
    """Шаг 3: Выбор категории и получение списка каналов."""
    print("\n>>> Шаг 3: Получение списка каналов...")
    category = iframe.get_by_text("Новости и политика").first
    await category.wait_for(state="visible", timeout=10000)
    await category.click()
    await asyncio.sleep(2)
    channel_buttons = await iframe.get_by_role("button").all()
    print(f"Найдено кнопок в iframe: {len(channel_buttons)}")
    return channel_buttons

async def parse_publication_details(post_el, source_id: str) -> Publication:
    """Парсинг всех доступных метаданных из элемента сообщения."""
    # Текст (используем устойчивый селектор)
    content_el = await query_selector_svelte(post_el, 'text')
    content = await content_el.inner_text() if content_el else ""
    
    # Время (мета)
    time_el = await query_selector_svelte(post_el, 'meta')
    time_text = await time_el.inner_text() if time_el else ""
    
    # Лайки/Реакции
    likes = 0
    reaction_els = await query_selector_all_svelte(post_el, 'reaction')
    for rel in reaction_els:
        counter_el = await query_selector_svelte(rel, 'counter')
        if counter_el:
            c_text = await counter_el.inner_text()
            likes += int(c_text) if c_text.isdigit() else 0

    # Медиа
    media = []
    img_els = await query_selector_all_svelte(post_el, 'img', ['image'])
    for img in img_els:
        src = await img.get_attribute('src')
        if src: media.append(src)

    # Просмотры (если есть в верстке, обычно рядом с временем)
    views = 0 # В текущей верстке MAX просмотры могут быть не видны явно без наведения

    return Publication(
        id=f"{source_id}_{int(time.time())}_{hash(content[:20])}",
        title=content[:50].replace('\n', ' '),
        content=content,
        source_id=source_id,
        source_type="max",
        published_ts=int(time.time()), # Упрощенно для отладки
        likes=likes,
        views=views,
        media=media,
        url="", # Ссылка на конкретный пост в MAX часто динамическая
        reposts=0,
        comments=0
    )

async def step_4_parse_channel_full(page, iframe, channel_buttons, index=1):
    """Шаг 4: Полный парсинг канала с формированием PublicationResponse."""
    print(f"\n>>> Шаг 4: Полный парсинг канала под индексом {index}...")
    target_btn = channel_buttons[index]
    source_id = await target_btn.get_attribute("name") or f"channel_{index}"
    
    await target_btn.click()
    await asyncio.sleep(3)
    
    # Используем устойчивый селектор
    posts_els = await query_selector_all_svelte(page, 'bubble')
    if not posts_els:
        posts_els = await query_selector_all_svelte(iframe, 'bubble')
    
    publications = []
    total_likes = 0
    
    for el in posts_els[:10]: # Берем 10 для примера
        pub = await parse_publication_details(el, source_id)
        publications.append(pub)
        total_likes += (pub.likes or 0)
        print(f"Парсинг поста: {pub.title[:30]}... (Лайков: {pub.likes})")

    response = PublicationResponse(
        publications=publications,
        aggregations={
            "stats": {
                "total_count": len(publications),
                "total_likes": total_likes
            }
        }
    )
    
    print("\nСформирован PublicationResponse:")
    print(f"Всего постов: {response.aggregations['stats']['total_count']}")
    print(f"Всего лайков: {response.aggregations['stats']['total_likes']}")
    return response

async def main():
    p_instance, ctx = None, None
    try:
        p_instance, ctx, page = await step_1_init()
        iframe = await step_2_navigate(page)
        channel_buttons = await step_3_list_channels(iframe)
        response = await step_4_parse_channel_full(page, iframe, channel_buttons)
        
        print("\nОтладка завершена. Данные получены.")
        input("\nНажмите Enter для выхода...")
    except Exception as e:
        print(f"\nОшибка: {e}")
    finally:
        if ctx: await ctx.close()
        if p_instance: await p_instance.stop()

if __name__ == "__main__":
    asyncio.run(main())

