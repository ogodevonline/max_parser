import asyncio
from playwright.async_api import async_playwright
from src.config import settings

async def open_codegen():
    """Запуск Playwright Codegen с сохранением сессии."""
    async with async_playwright() as p:
        # Запускаем браузер с вашей сессией и открываем инспектор (codegen)
        # Это позволит вам кликать по элементам, а Playwright будет показывать селекторы
        args = [
            f"--user-data-dir={settings.USER_DATA_DIR}",
            settings.BASE_URL
        ]
        
        print(f"Запускаю codegen для {settings.BASE_URL}...")
        print("Используется сессия из:", settings.USER_DATA_DIR)
        
        # Выполняем команду codegen через subprocess, так как это CLI инструмент
        process = await asyncio.create_subprocess_exec(
            "uv", "run", "playwright", "codegen", 
            "--load-storage=storage/auth.json", # Если бы мы использовали json
            "--save-storage=storage/auth.json",
            settings.BASE_URL,
            # Для использования именно папки user_data_dir в codegen:
            # playwright codegen --user-data-dir=...
        )
        
        # Но проще запустить через shell команду напрямую
        cmd = f"uv run playwright codegen --user-data-dir={settings.USER_DATA_DIR} {settings.BASE_URL}"
        print(f"Выполните в терминале:\n\n{cmd}\n")

if __name__ == "__main__":
    # Самый простой способ для пользователя - просто дать команду
    from src.config import settings
    print("\nЧтобы открыть UI инспектор с вашей сессией, выполните команду:\n")
    print(f"uv run playwright codegen --user-data-dir={settings.USER_DATA_DIR} {settings.BASE_URL}")
    print("\nВ открывшемся окне вы сможете нажимать на элементы и видеть их селекторы.")
