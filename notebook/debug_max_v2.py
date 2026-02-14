import os
import sys
import asyncio
import sqlite3
from playwright.async_api import async_playwright

# Добавляем корень проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import settings
from src.handlers.max_parser_utils import parse_max_publication, create_publication_response
from src.db.publication_dao import PublicationDAO
from src.handlers.svelte_selectors import query_selector_all_svelte

async def run_debug_v2():
    print("\n>>> Запуск отладки v2 (с вынесенной логикой и БД)...")
    
    async with async_playwright() as p:
        # 1. Инициализация
        user_data = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', settings.USER_DATA_DIR))
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data,
            headless=False,
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()
        await page.goto(settings.BASE_URL)
        print(f"Открыта страница: {page.url}")
        
        input("\nНажмите Enter после того как убедитесь, что страница загружена...")

        # 2. Навигация к каналам
        await page.get_by_role("textbox", name="Поиск").click()
        await page.get_by_role("button", name="Каналы").click()
        
        iframe_locator = page.locator('iframe[title="webapp"]')
        await iframe_locator.wait_for(state="visible", timeout=15000)
        iframe = iframe_locator.content_frame
        print("Iframe webapp найден")

        # 3. Выбор категории
        category = iframe.get_by_text("Новости и политика").first
        await category.wait_for(state="visible")
        await category.click()
        print("Категория выбрана")
        await asyncio.sleep(2)

        # 4. Выбор канала
        channel_buttons = await iframe.get_by_role("button").all()
        target_btn = channel_buttons[1] # Берем второй канал для теста
        source_id = await target_btn.get_attribute("name") or "test_channel"
        print(f"Открываем канал: {source_id}")
        await target_btn.click()
        await asyncio.sleep(3)

        # 5. Парсинг публикаций (используем устойчивый селектор)
        posts_els = await query_selector_all_svelte(page, 'bubble')
        if not posts_els:
            posts_els = await query_selector_all_svelte(iframe, 'bubble')
        
        print(f"Найдено элементов для парсинга: {len(posts_els)}")
        
        publications = []
        dao = PublicationDAO()
        
        for el in posts_els[:5]: # Парсим первые 5
            pub = await parse_max_publication(el, source_id)
            publications.append(pub)
            
            # Проверка сохранения в БД
            await dao.save_publication(pub)
            print(f"  - Спарсен и сохранен пост: {pub.title[:40]}... [Лайки: {pub.likes}]")

        # 6. Формирование финального ответа
        response = await create_publication_response(publications)
        
        print("\n>>> Итоговый результат (PublicationResponse):")
        print(f"Количество: {response.aggregations['stats']['total_count']}")
        print(f"Всего лайков: {response.aggregations['stats']['total_likes']}")
        
        # 7. Проверка данных в БД через прямой запрос
        print("\n>>> Проверка данных в SQLite...")
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', "storage/publications.db"))
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM publications WHERE source_id = ?", (source_id,))
            count = cursor.fetchone()[0]
            print(f"Записей в БД для {source_id}: {count}")
        
        input("\nНажмите Enter для завершения и закрытия браузера...")
        await context.close()

if __name__ == "__main__":
    asyncio.run(run_debug_v2())
