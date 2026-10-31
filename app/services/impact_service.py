from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from app.models import MarketAlert


HIGH_IMPACT_KEYWORDS = {
    "nfp": 95,
    "nonfarm payroll": 95,
    "cpi": 90,
    "core cpi": 90,
    "federal reserve": 92,
    "fed": 92,
    "fomc": 92,
    "ecb": 88,
    "boj": 88,
    "boe": 88,
    "inflation": 88,
    "rate decision": 90,
    "gdp": 84,
    "pmi": 82,
    "retail sales": 80,
    "btc": 78,
    "bitcoin": 78,
    "ethereum": 76,
    "etf": 75,
    "regulation": 74,
}


def score_impact(alert: MarketAlert) -> int:
    title = alert.title.lower()
    score = 0
    for keyword, weight in HIGH_IMPACT_KEYWORDS.items():
        if keyword in title:
            score += weight
    if alert.category == "forex":
        score += 10
    if alert.category == "crypto":
        score += 6
    if alert.source.lower() in {"forexfactory", "tradingeconomics", "reuters", "bloomberg"}:
        score += 8
    return min(score, 100)


def classify_market(title: str) -> str:
    lower = title.lower()
    if any(token in lower for token in ["bitcoin", "btc", "ethereum", "eth", "crypto", "cryptoasset", "coinbase", "etf"]):
        return "crypto"
    if any(token in lower for token in ["eur/usd", "gbp/usd", "usd/jpy", "usd/cad", "forex", "cpi", "nfp", "fed", "ecb", "boj", "boe"]):
        return "forex"
    return "macro"


def build_demo_alerts() -> List[MarketAlert]:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    alerts = [
        MarketAlert(
            title="US NFP blows past expectations as payrolls surge",
            source="ForexFactory",
            category="forex",
            asset_tags=["USD", "EUR/USD", "GBP/USD"],
            summary="Strong labor data tightens the outlook for rate policy and lifts the US dollar.",
            url="https://www.forexfactory.com/",
            impact_score=95,
            published_at=now,
        ),
        MarketAlert(
            title="CPI reads hotter than expected, inflation remains sticky",
            source="TradingEconomics",
            category="forex",
            asset_tags=["USD", "EUR/USD", "DXY"],
            summary="Headline inflation exceeds forecast and markets revise expectations for central bank policy.",
            url="https://tradingeconomics.com/",
            impact_score=90,
            published_at=now,
        ),
        MarketAlert(
            title="Bitcoin ETF inflows accelerate as institutional appetite returns",
            source="CoinDesk",
            category="crypto",
            asset_tags=["BTC", "ETH", "ETF"],
            summary="Spot ETF demand remains strong and supports a risk-on tone across digital assets.",
            url="https://www.coindesk.com/",
            impact_score=78,
            published_at=now,
        ),
        MarketAlert(
            title="ECB rate decision prompts euro volatility across major pairs",
            source="Reuters",
            category="forex",
            asset_tags=["EUR", "EUR/USD", "USD/JPY"],
            summary="The central bank guidance shifts euro sentiment and creates higher volatility for FX traders.",
            url="https://www.reuters.com/",
            impact_score=88,
            published_at=now,
        ),
    ]
    for alert in alerts:
        alert.impact_score = score_impact(alert)
        alert.category = classify_market(alert.title)
    return alerts
