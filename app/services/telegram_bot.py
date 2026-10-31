from __future__ import annotations

import logging
from typing import List

import feedparser

from app.models import MarketAlert
from app.services.impact_service import build_demo_alerts, build_forex_event_alerts, score_impact, classify_market

logger = logging.getLogger(__name__)


def get_demo_news() -> List[MarketAlert]:
    alerts = build_demo_alerts() + build_forex_event_alerts()
    for item in alerts:
        item.impact_score = score_impact(item)
        item.category = classify_market(item.title)
    return alerts


def fetch_rss_news(source_url: str, default_category: str = "macro") -> List[MarketAlert]:
    try:
        feed = feedparser.parse(source_url)
    except Exception as exc:
        logger.warning("RSS parse failed for %s: %s", source_url, exc)
        return []

    items: List[MarketAlert] = []
    for entry in getattr(feed, "entries", [])[:10]:
        title = getattr(entry, "title", "Untitled")
        link = getattr(entry, "link", "")
        summary = getattr(entry, "summary", "")
        item = MarketAlert(
            title=str(title),
            source=(source_url.split("//")[-1].split("/")[0] if "//" in source_url else "rss"),
            category=default_category,
            asset_tags=[],
            summary=str(summary)[:300],
            url=str(link),
            impact_score=0,
            published_at=getattr(entry, "published", ""),
        )
        item.impact_score = score_impact(item)
        item.category = classify_market(item.title)
        items.append(item)
    return items


def filter_high_impact(news_items: List[MarketAlert], minimum_score: int = 75) -> List[MarketAlert]:
    return [item for item in news_items if item.impact_score >= minimum_score]


def explain_alert(item: MarketAlert) -> str:
    assets = ", ".join(item.asset_tags) if item.asset_tags else "General"
    return f"{item.title}\nSource: {item.source}\nImpact: {item.impact_score}/100\nAssets: {assets}"


def get_live_market_alerts() -> List[MarketAlert]:
    combined: List[MarketAlert] = []
    combined.extend(get_demo_news())
    for source_url in [
        "https://www.fxstreet.com/rss",
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://www.forexfactory.com/ffcal.xml",
    ]:
        try:
            category = "forex" if "fx" in source_url or "forex" in source_url else "crypto"
            combined.extend(fetch_rss_news(source_url, default_category=category))
        except Exception as exc:
            logger.warning("Could not load source %s: %s", source_url, exc)
    seen = set()
    deduped: List[MarketAlert] = []
    for item in combined:
        key = (item.title.lower(), item.source.lower())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped
