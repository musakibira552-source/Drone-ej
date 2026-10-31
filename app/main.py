from __future__ import annotations

from typing import List

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from app.config import settings
from app.models import UserWatchlist
from app.services.news_service import explain_alert, filter_high_impact, get_live_market_alerts

USER_WATCHLISTS: dict[int, UserWatchlist] = {}


def _check_allowed(update: Update) -> bool:
    if not settings.ALLOWED_TELEGRAM_USER_IDS:
        return True
    return update.effective_user.id in settings.ALLOWED_TELEGRAM_USER_IDS


async def _reply_access_denied(update: Update) -> None:
    await update.message.reply_text("Access denied. Your Telegram user ID is not allowed to use this bot.")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _check_allowed(update):
        await _reply_access_denied(update)
        return

    chat_id = update.effective_chat.id
    USER_WATCHLISTS.setdefault(chat_id, UserWatchlist(chat_id=chat_id, assets=settings.DEFAULT_WATCHLIST))
    await update.message.reply_text(
        "Hi! I’m Drone-ej. I scan forex and crypto market news and flag high-impact events.\n\n"
        "Available commands:\n"
        "• /start\n"
        "• /help\n"
        "• /watchlist\n"
        "• /demo\n"
        "• /add BTC\n"
        "• /remove ETH\n"
        "• /clear"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _check_allowed(update):
        await _reply_access_denied(update)
        return

    await update.message.reply_text(
        "I monitor: BTC, ETH, EUR/USD, USD/JPY, GBP/USD, XAU/USD and key macro events like CPI, NFP, FOMC, ECB, BoE, and BoJ.\n\n"
        "Use /watchlist to see assets, /add <symbol> to add one, /remove <symbol> to remove one, /demo for sample alerts, and /clear to reset your context."
    )


async def watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _check_allowed(update):
        await _reply_access_denied(update)
        return

    chat_id = update.effective_chat.id
    watchlist = USER_WATCHLISTS.setdefault(chat_id, UserWatchlist(chat_id=chat_id, assets=settings.DEFAULT_WATCHLIST))
    await update.message.reply_text(f"Your watchlist: {', '.join(watchlist.assets)}")


async def add_watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _check_allowed(update):
        await _reply_access_denied(update)
        return

    chat_id = update.effective_chat.id
    watchlist = USER_WATCHLISTS.setdefault(chat_id, UserWatchlist(chat_id=chat_id, assets=settings.DEFAULT_WATCHLIST))
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /add BTC or /add EUR/USD")
        return

    asset = context.args[0].strip().upper()
    if asset not in watchlist.assets:
        watchlist.assets.append(asset)
    await update.message.reply_text(f"Added {asset} to your watchlist.")


async def remove_watchlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _check_allowed(update):
        await _reply_access_denied(update)
        return

    chat_id = update.effective_chat.id
    watchlist = USER_WATCHLISTS.setdefault(chat_id, UserWatchlist(chat_id=chat_id, assets=settings.DEFAULT_WATCHLIST))
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /remove BTC or /remove EUR/USD")
        return

    asset = context.args[0].strip().upper()
    if asset in watchlist.assets:
        watchlist.assets.remove(asset)
    await update.message.reply_text(f"Removed {asset} from your watchlist.")


async def demo_news_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _check_allowed(update):
        await _reply_access_denied(update)
        return

    alerts = filter_high_impact(get_live_market_alerts(), minimum_score=75)
    if not alerts:
        await update.message.reply_text("No high-impact alerts available right now.")
        return

    message = "\n\n".join(explain_alert(alert) for alert in alerts[:5])
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _check_allowed(update):
        await _reply_access_denied(update)
        return

    chat_id = update.effective_chat.id
    USER_WATCHLISTS[chat_id] = UserWatchlist(chat_id=chat_id, assets=settings.DEFAULT_WATCHLIST)
    await update.message.reply_text("Your watchlist and chat state were reset.")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _check_allowed(update):
        await _reply_access_denied(update)
        return

    text = update.message.text or ""
    if not text or text.startswith("/"):
        return

    watchlist = USER_WATCHLISTS.setdefault(update.effective_chat.id, UserWatchlist(chat_id=update.effective_chat.id, assets=settings.DEFAULT_WATCHLIST))
    if any(token.lower() in text.lower() for token in ["btc", "eth", "eur/usd", "usd/jpy", "nfp", "cpi", "fomc", "ecb", "boe"]):
        alerts = filter_high_impact(get_live_market_alerts(), minimum_score=75)
        filtered = [alert for alert in alerts if any(asset.lower() in text.lower() for asset in alert.asset_tags) or any(keyword.lower() in alert.title.lower() for keyword in text.lower().split())]
        if filtered:
            message = "\n\n".join(explain_alert(alert) for alert in filtered[:3])
            await update.message.reply_text(message)
            return

    await update.message.reply_text(
        "I’m a market intelligence bot. Try /demo for sample alerts, /watchlist to see your symbols, or /help for commands."
    )


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
        application.add_handler(CommandHandler("add", add_watchlist_command))
        application.add_handler(CommandHandler("remove", remove_watchlist_command))
        application.add_handler(CommandHandler("demo", demo_news_command))
        application.add_handler(CommandHandler("clear", clear_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        return application
