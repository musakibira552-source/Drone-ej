import os
from typing import List


class Settings:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
    APP_ENV = os.getenv("APP_ENV", "development")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/drone_ej")
    DEFAULT_WATCHLIST = [item.strip() for item in os.getenv("DEFAULT_WATCHLIST", "BTC,ETH,EUR/USD,USD/JPY,GBP/USD").split(",") if item.strip()]
    ALLOWED_TELEGRAM_USER_IDS = [int(item.strip()) for item in os.getenv("ALLOWED_TELEGRAM_USER_IDS", "").split(",") if item.strip()]
    NEWS_REFRESH_SECONDS = int(os.getenv("NEWS_REFRESH_SECONDS", "180"))


settings = Settings()
