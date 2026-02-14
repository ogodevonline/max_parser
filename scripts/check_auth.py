import asyncio
from playwright.async_api import async_playwright
from src.config import settings

async def check_auth():
    """Скрипт для проверки авторизации и ручного входа."""
    async with async_playwright() as p:
        # Запускаем браузер с сохранением сессии
        context = await p.chromium.launch_persistent_context(
            user_data_dir=settings.USER_DATA_DIR,
            headless=False,
            viewport={'width': 1280, 'height': 720}
        )
        
        page = await context.new_page()
        await page.goto(settings.BASE_URL)
        
        print(f"Открыта страница: {settings.BASE_URL}")
        print("Если вы не авторизованы, пройдите авторизацию в открывшемся окне.")
        print("После завершения закройте браузер или нажмите Ctrl+C в терминале.")
        
        try:
            # Ждем бесконечно, пока пользователь не закроет браузер
            while True:
                await asyncio.sleep(1)
                if page.is_closed():
                    break
        except KeyboardInterrupt:
            print("\nЗавершение работы...")
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(check_auth())
