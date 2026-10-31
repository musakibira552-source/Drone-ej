from __future__ import annotations

from typing import List

from app.models import MarketAlert
from app.services.impact_service import build_demo_alerts


def get_demo_news() -> List[MarketAlert]:
    return build_demo_alerts()


def filter_high_impact(news_items: List[MarketAlert], minimum_score: int = 75) -> List[MarketAlert]:
    return [item for item in news_items if item.impact_score >= minimum_score]


def explain_alert(item: MarketAlert) -> str:
    return f"{item.title} | Source: {item.source} | Impact: {item.impact_score}/100 | Assets: {', '.join(item.asset_tags) if item.asset_tags else 'General'}"
