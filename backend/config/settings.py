from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Базовый путь проекта
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    # Настройки базы данных
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/electro_db"

    # Настройки приложения
    APP_NAME: str = "СТ АВТО учет показаний эл. энергии"
    DEBUG: bool = True

    # Настройки безопасности (JWT)
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Настройки фронтенда
    FRONTEND_URL: str = "http://localhost:3000"

    # Настройки суперпользователя (опционально)
    SUPERUSER_USERNAME: str | None = None
    SUPERUSER_PASSWORD: str | None = None
    SUPERUSER_EMAIL: str | None = None
    SUPERUSER_PLOT_NUMBER: str | None = None

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

settings = Settings()