from __future__ import annotations

import asyncio
import logging

from app.config import settings
from app.services.telegram_bot import TelegramBot


logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO), format="%(asctime)s - %(levelname)s - %(message)s")


async def main() -> None:
    bot = TelegramBot(settings.TELEGRAM_TOKEN)
    application = await bot.build()
    logging.info("Drone-ej bot is starting...")
    await application.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
