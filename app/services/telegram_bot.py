from __future__ import annotations

import os
from typing import List

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from app.config import settings
from app.models import UserWatchlist
from app.services.news_service import explain_alert, filter_high_impact, get_demo_news


USER_WATCHLISTS: dict[int, UserWatchlist] = {}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    USER_WATCHLISTS.setdefault(chat_id, UserWatchlist(chat_id=chat_id, assets=settings.DEFAULT_WATCHLIST))
    await update.message.reply_text(
        "Hi! I’m Drone-ej. I scan forex and crypto market news and flag high-impact events.\n\n"
        "Available commands:\n"
        "• /start\n"
        "• /help\n"
        "• /watchlist\n"
        "• /demo\n"
        "• /clear"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "I monitor: BTC, ETH, EUR/USD, USD/JPY, GBP/USD, and key macro events like CPI, NFP, FOMC, ECB, BoE, and BoJ.\n\n"
        "Use /watchlist to see assets, /demo to preview market alerts, and /clear to reset your context."
    )


async def watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    watchlist = USER_WATCHLISTS.setdefault(chat_id, UserWatchlist(chat_id=chat_id, assets=settings.DEFAULT_WATCHLIST))
    await update.message.reply_text(f"Your watchlist: {', '.join(watchlist.assets)}")


async def demo_news_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    alerts = filter_high_impact(get_demo_news(), minimum_score=75)
    if not alerts:
        await update.message.reply_text("No high-impact alerts available right now.")
        return

    message = "\n\n".join(explain_alert(alert) for alert in alerts)
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    USER_WATCHLISTS[chat_id] = UserWatchlist(chat_id=chat_id, assets=settings.DEFAULT_WATCHLIST)
    await update.message.reply_text("Your watchlist and chat state were reset.")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or ""
    if not text:
        return
    if text.startswith("/"):
        return

    response = (
        "I’m a market intelligence bot. Send /demo to see sample alerts, /watchlist to view your symbols, or /help for more commands."
    )
    await update.message.reply_text(response)


class TelegramBot:
    def __init__(self, token: str) -> None:
        self.token = token

    async def build(self) -> Application:
        if not self.token:
            raise ValueError("TELEGRAM_TOKEN is missing. Add it to your .env file before starting the bot.")

        application = Application.builder().token(self.token).build()
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("watchlist", watchlist_command))
        application.add_handler(CommandHandler("demo", demo_news_command))
        application.add_handler(CommandHandler("clear", clear_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        return application
