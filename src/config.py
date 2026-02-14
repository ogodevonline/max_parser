from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфигурация приложения с использованием pydantic-settings."""

    BASE_URL: str = "https://web.max.ru/"
    USER_DATA_DIR: str = "./storage/user_data"
    HEADLESS: bool = False
    DEFAULT_LANGUAGE: str = "ru-RU"
    VIEWPORT_WIDTH: int = 1920
    VIEWPORT_HEIGHT: int = 1080

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
